"""Service for handling bulk character operations."""
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from uuid import UUID, uuid4
import asyncio
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from character_service.core.exceptions import ValidationError
from character_service.domain.character import Character
from character_service.domain.theme import Theme
from character_service.services.character import CharacterService
from character_service.services.theme_transition import ThemeTransitionService
from character_service.services.validation import ValidationService
from character_service.api.v2.models.bulk import (
    BulkOperationStatus,
    BulkValidationError,
    ValidationResult,
)


class BulkOperationService:
    """Service for handling bulk character operations."""

    def __init__(
        self,
        session: AsyncSession,
        character_service: Optional[CharacterService] = None,
        theme_service: Optional[ThemeTransitionService] = None,
        validation_service: Optional[ValidationService] = None,
    ):
        """Initialize the service.

        Args:
            session: Database session
            character_service: Optional character service
            theme_service: Optional theme service
            validation_service: Optional validation service
        """
        self.session = session
        self.character_service = character_service or CharacterService(session)
        self.theme_service = theme_service or ThemeTransitionService(session)
        self.validation_service = validation_service or ValidationService(session)
        self._max_parallel = 5  # Maximum parallel operations
        self._active_batches: Dict[UUID, BulkOperationStatus] = {}

    async def create_characters(
        self,
        characters: List[Dict[str, Any]],
        batch_label: Optional[str] = None,
        campaign_id: Optional[UUID] = None,
        theme_id: Optional[UUID] = None,
        created_by: str = "system",
    ) -> Tuple[UUID, BulkOperationStatus]:
        """Create multiple characters in bulk.

        Args:
            characters: List of character data
            batch_label: Optional batch label
            campaign_id: Optional campaign ID
            theme_id: Optional theme ID
            created_by: Who/what is creating the characters

        Returns:
            Tuple of (batch_id, initial_status)
        """
        batch_id = uuid4()
        status = BulkOperationStatus(
            batch_id=batch_id,
            status="pending",
            progress=0.0,
            total_count=len(characters),
            processed_count=0,
            success_count=0,
            error_count=0,
            created=[],
            errors=[],
            started_at=datetime.utcnow().isoformat(),
        )
        self._active_batches[batch_id] = status

        # Start async processing
        asyncio.create_task(
            self._process_batch(
                batch_id=batch_id,
                characters=characters,
                campaign_id=campaign_id,
                theme_id=theme_id,
                created_by=created_by,
            )
        )

        return batch_id, status

    async def validate_characters(
        self,
        characters: List[Dict[str, Any]],
        campaign_id: Optional[UUID] = None,
        theme_id: Optional[UUID] = None,
        validation_rules: Optional[List[str]] = None,
    ) -> List[ValidationResult]:
        """Validate multiple characters in parallel.

        Args:
            characters: List of character data
            campaign_id: Optional campaign ID
            theme_id: Optional theme ID
            validation_rules: Optional specific rules to validate

        Returns:
            List of validation results
        """
        results: List[ValidationResult] = []
        
        # Create validation tasks
        tasks = []
        semaphore = asyncio.Semaphore(self._max_parallel)

        for idx, char_data in enumerate(characters):
            task = self._validate_character(
                index=idx,
                data=char_data,
                campaign_id=campaign_id,
                theme_id=theme_id,
                validation_rules=validation_rules or [],
                semaphore=semaphore,
            )
            tasks.append(task)

        # Run validations in parallel
        validation_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for idx, result in enumerate(validation_results):
            if isinstance(result, Exception):
                # Handle validation errors
                results.append(
                    ValidationResult(
                        index=idx,
                        is_valid=False,
                        errors=[
                            {
                                "error_type": "validation_error",
                                "message": str(result),
                            }
                        ],
                        warnings=[],
                    )
                )
            else:
                results.append(result)

        return results

    async def get_operation_status(
        self,
        batch_id: UUID,
    ) -> Optional[BulkOperationStatus]:
        """Get status of a bulk operation.

        Args:
            batch_id: The batch ID to check

        Returns:
            Operation status if found
        """
        return self._active_batches.get(batch_id)

    async def _process_batch(
        self,
        batch_id: UUID,
        characters: List[Dict[str, Any]],
        campaign_id: Optional[UUID] = None,
        theme_id: Optional[UUID] = None,
        created_by: str = "system",
    ) -> None:
        """Process a batch of character creations.

        Args:
            batch_id: The batch ID
            characters: List of character data
            campaign_id: Optional campaign ID
            theme_id: Optional theme ID
            created_by: Who/what is creating the characters
        """
        status = self._active_batches[batch_id]
        status.status = "processing"

        try:
            # Process in chunks to control memory usage
            chunk_size = 10
            for i in range(0, len(characters), chunk_size):
                chunk = characters[i:i + chunk_size]
                
                # Create validation tasks
                tasks = []
                semaphore = asyncio.Semaphore(self._max_parallel)

                for idx, char_data in enumerate(chunk, start=i):
                    task = self._create_character(
                        index=idx,
                        data=char_data,
                        campaign_id=campaign_id,
                        theme_id=theme_id,
                        created_by=created_by,
                        semaphore=semaphore,
                    )
                    tasks.append(task)

                # Process chunk
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Update status
                for result in results:
                    status.processed_count += 1
                    if isinstance(result, tuple):
                        # Successful creation
                        char_response, _ = result
                        status.success_count += 1
                        status.created.append(char_response)
                    else:
                        # Error
                        status.error_count += 1
                        if isinstance(result, Exception):
                            error = BulkValidationError(
                                index=i,
                                errors=[
                                    {
                                        "error_type": "creation_error",
                                        "message": str(result),
                                    }
                                ],
                            )
                            status.errors.append(error)

                status.progress = status.processed_count / status.total_count

            status.status = "completed"
            status.completed_at = datetime.utcnow().isoformat()

        except Exception as e:
            status.status = "failed"
            status.completed_at = datetime.utcnow().isoformat()
            status.errors.append(
                BulkValidationError(
                    index=-1,
                    errors=[
                        {
                            "error_type": "batch_error",
                            "message": f"Batch processing failed: {str(e)}",
                        }
                    ],
                )
            )

    async def _validate_character(
        self,
        index: int,
        data: Dict[str, Any],
        campaign_id: Optional[UUID] = None,
        theme_id: Optional[UUID] = None,
        validation_rules: List[str] = None,
        semaphore: asyncio.Semaphore = None,
    ) -> ValidationResult:
        """Validate a single character.

        Args:
            index: Character index in batch
            data: Character data
            campaign_id: Optional campaign ID
            theme_id: Optional theme ID
            validation_rules: Optional specific rules to validate
            semaphore: Semaphore for parallel processing

        Returns:
            Validation result
        """
        if semaphore:
            async with semaphore:
                return await self._do_validate_character(
                    index=index,
                    data=data,
                    campaign_id=campaign_id,
                    theme_id=theme_id,
                    validation_rules=validation_rules,
                )
        else:
            return await self._do_validate_character(
                index=index,
                data=data,
                campaign_id=campaign_id,
                theme_id=theme_id,
                validation_rules=validation_rules,
            )

    async def _do_validate_character(
        self,
        index: int,
        data: Dict[str, Any],
        campaign_id: Optional[UUID] = None,
        theme_id: Optional[UUID] = None,
        validation_rules: Optional[List[str]] = None,
    ) -> ValidationResult:
        """Perform character validation.

        Args:
            index: Character index in batch
            data: Character data
            campaign_id: Optional campaign ID
            theme_id: Optional theme ID
            validation_rules: Optional specific rules to validate

        Returns:
            Validation result
        """
        try:
            # Add campaign and theme context if provided
            if campaign_id:
                data["campaign_id"] = campaign_id
            if theme_id:
                data["theme_id"] = theme_id

            # Validate character data
            validation_result = await self.validation_service.validate_character(
                data=data,
                rules=validation_rules,
            )

            return ValidationResult(
                index=index,
                is_valid=validation_result.is_valid,
                errors=validation_result.errors,
                warnings=validation_result.warnings,
            )

        except Exception as e:
            return ValidationResult(
                index=index,
                is_valid=False,
                errors=[
                    {
                        "error_type": "validation_error",
                        "message": str(e),
                    }
                ],
                warnings=[],
            )

    async def _create_character(
        self,
        index: int,
        data: Dict[str, Any],
        campaign_id: Optional[UUID] = None,
        theme_id: Optional[UUID] = None,
        created_by: str = "system",
        semaphore: asyncio.Semaphore = None,
    ) -> Tuple[Dict[str, Any], Character]:
        """Create a single character.

        Args:
            index: Character index in batch
            data: Character data
            campaign_id: Optional campaign ID
            theme_id: Optional theme ID
            created_by: Who/what is creating the character
            semaphore: Semaphore for parallel processing

        Returns:
            Tuple of (response_data, character)

        Raises:
            ValidationError: If validation fails
        """
        if semaphore:
            async with semaphore:
                return await self._do_create_character(
                    index=index,
                    data=data,
                    campaign_id=campaign_id,
                    theme_id=theme_id,
                    created_by=created_by,
                )
        else:
            return await self._do_create_character(
                index=index,
                data=data,
                campaign_id=campaign_id,
                theme_id=theme_id,
                created_by=created_by,
            )

    async def _do_create_character(
        self,
        index: int,
        data: Dict[str, Any],
        campaign_id: Optional[UUID] = None,
        theme_id: Optional[UUID] = None,
        created_by: str = "system",
    ) -> Tuple[Dict[str, Any], Character]:
        """Perform character creation.

        Args:
            index: Character index in batch
            data: Character data
            campaign_id: Optional campaign ID
            theme_id: Optional theme ID
            created_by: Who/what is creating the character

        Returns:
            Tuple of (response_data, character)

        Raises:
            ValidationError: If validation fails
        """
        # Add campaign and theme context if provided
        if campaign_id:
            data["campaign_id"] = campaign_id
        if theme_id:
            data["theme_id"] = theme_id

        # Create character
        character = await self.character_service.create_character(
            data=data,
            created_by=created_by,
        )

        # Apply theme if provided
        if theme_id:
            await self.theme_service.apply_transition(
                character_id=character.id,
                from_theme_id=None,
                to_theme_id=theme_id,
                transition_type="creation",
            )

        # Prepare response
        response = {
            "id": character.id,
            "name": character.name,
            "level": character.level,
            "class_name": character.class_name,
            "race": character.race,
            "campaign_id": character.campaign_id,
            "theme_id": theme_id if theme_id else None,
            "created_at": character.created_at.isoformat(),
            "created_by": character.created_by,
        }

        return response, character
