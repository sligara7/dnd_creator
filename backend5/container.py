from typing import Dict, Any
import logging

# Domain Services
from domain.services.character_builder import CharacterBuilderService
from domain.services.validation_service import ValidationService
from domain.services.level_progression_service import LevelProgressionService

# Infrastructure
from infrastructure.data.character_repository_impl import CharacterRepositoryImpl
from infrastructure.llm.ollama_llm_service import OllamaLLMService
from infrastructure.data.character_storage import CharacterStorage

# Application Use Cases
from application.use_cases.create_character import CreateCharacterUseCase
from application.use_cases.create_progression import CreateProgressionUseCase
from application.use_cases.validate_character import ValidateCharacterUseCase

# Interfaces
from interfaces.cli.character_creator_cli import CharacterCreatorCLI
from interfaces.cli.cli_utils import CLIFormatter

logger = logging.getLogger(__name__)

class DIContainer:
    """Dependency injection container for the application."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._configure_dependencies()
    
    def _configure_dependencies(self) -> None:
        """Configure all application dependencies."""
        
        # Infrastructure Layer
        self._services['llm_service'] = OllamaLLMService(model="llama3")
        self._services['character_repository'] = CharacterRepositoryImpl()
        self._services['character_storage'] = CharacterStorage()
        
        # Domain Services
        self._services['character_builder'] = CharacterBuilderService()
        self._services['validation_service'] = ValidationService()
        self._services['level_progression_service'] = LevelProgressionService()
        
        # Application Use Cases
        self._services['create_character_use_case'] = CreateCharacterUseCase(
            character_builder=self.get('character_builder'),
            validation_service=self.get('validation_service'),
            character_repository=self.get('character_repository')
        )
        
        self._services['create_progression_use_case'] = CreateProgressionUseCase(
            character_builder=self.get('character_builder'),
            level_progression_service=self.get('level_progression_service'),
            llm_service=self.get('llm_service')
        )
        
        self._services['validate_character_use_case'] = ValidateCharacterUseCase(
            validation_service=self.get('validation_service')
        )
        
        # Interface Layer
        self._services['cli_formatter'] = CLIFormatter()
        self._services['character_creator_cli'] = CharacterCreatorCLI(
            create_character_use_case=self.get('create_character_use_case'),
            create_progression_use_case=self.get('create_progression_use_case'),
            validate_character_use_case=self.get('validate_character_use_case'),
            formatter=self.get('cli_formatter'),
            storage=self.get('character_storage')
        )
    
    def get(self, service_name: str) -> Any:
        """Get a service from the container."""
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not found")
        return self._services[service_name]
    
    # Add to existing container

    def _configure_dependencies(self) -> None:
        # ... existing dependencies ...
        
        # Validators
        from domain.validators.core_character_validator import CoreCharacterValidator
        from domain.validators.multiclass_validator import MulticlassValidator
        from domain.validators.optimization_validator import OptimizationValidator
        from infrastructure.validation.legacy_validator_adapter import LegacyValidatorAdapter
        
        validators = [
            CoreCharacterValidator(),
            MulticlassValidator(), 
            OptimizationValidator(),
            LegacyValidatorAdapter()
        ]
        
        # Validation Service
        self._services['validation_service'] = ValidationService(validators)
        
        # Validation Use Case
        self._services['validate_character_use_case'] = ValidateCharacterUseCase(
            validation_service=self.get('validation_service'),
            character_repository=self.get('character_repository')
        )