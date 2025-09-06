"""Image generation task worker."""

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from image_service.core.config import get_settings
from image_service.core.errors import (
    APIError,
    ProcessingError,
    ValidationError,
    with_retry,
    rate_limit_handler,
    RetryConfig,
)
from image_service.core.logging import get_logger
from image_service.integration.getimg import GetImgClient
from image_service.services.queue import AsyncQueueService

settings = get_settings()
logger = get_logger(__name__)


class GenerationWorker:
    """Worker for processing image generation tasks."""

    def __init__(
        self,
        queue_service: AsyncQueueService,
        getimg_client: GetImgClient,
        max_concurrent: int = settings.MAX_CONCURRENT_GENERATIONS,
        poll_interval: float = 1.0,
    ):
        """Initialize worker."""
        self.queue = queue_service
        self.getimg = getimg_client
        self.max_concurrent = max_concurrent
        self.poll_interval = poll_interval
        self.running = False
        self.tasks: List[asyncio.Task] = []

    async def start(self) -> None:
        """Start the worker."""
        self.running = True
        logger.info("Generation worker starting")

        try:
            while self.running:
                # Clean up completed tasks
                self.tasks = [t for t in self.tasks if not t.done()]

                # Check if we can process more tasks
                if len(self.tasks) < self.max_concurrent:
                    # Get next task
                    task_data = await self.queue.get_next_task()
                    if task_data:
                        # Process task in background
                        task = asyncio.create_task(self.process_task(task_data))
                        self.tasks.append(task)
                    else:
                        # No tasks available, wait before polling again
                        await asyncio.sleep(self.poll_interval)
                else:
                    # At max concurrent tasks, wait for some to complete
                    await asyncio.sleep(self.poll_interval)

        except asyncio.CancelledError:
            logger.info("Generation worker shutting down")
            self.running = False
            # Cancel all running tasks
            for task in self.tasks:
                task.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)
        except Exception as e:
            logger.error("Worker error", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop the worker."""
        self.running = False
        # Wait for all tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("Generation worker stopped")

    def _validate_task_params(self, task_type: str, params: Dict[str, Any]) -> None:
        """Validate task parameters."""
        if task_type == "portrait":
            required = {"character", "theme", "style"}
        elif task_type == "map":
            required = {"theme", "features", "terrain"}
        elif task_type == "item":
            required = {"item", "theme", "style", "properties"}
        else:
            raise ValidationError(
                message=f"Unknown task type: {task_type}",
                field="type",
                value=task_type,
            )

        missing = required - set(params.keys())
        if missing:
            raise ValidationError(
                message=f"Missing required parameters: {', '.join(missing)}",
                field="params",
                value=list(missing),
            )

    @with_retry()
    async def process_task(self, task_data: Dict[str, Any]) -> None:
        """Process a single task."""
        task_id = task_data["id"]
        task_type = task_data["type"]
        params = task_data["params"]

        # Validate task data
        try:
            self._validate_task_params(task_type, params)
        except ValidationError as e:
            logger.error(
                "Task validation failed",
                task_id=task_id,
                error=str(e),
                field=e.details.get("field"),
            )
            await self.queue.fail_task(task_id, str(e), retry=False)
            return

        try:
            logger.info(
                "Processing task",
                task_id=task_id,
                type=task_type,
            )

            # Update progress
            await self.queue.update_task_progress(task_id, 0.0, "starting")

            # Process based on task type
            result = await self._handle_task(task_type, params, task_id)

            # Mark task as completed
            await self.queue.complete_task(task_id, result)

        except ValidationError as e:
            logger.error(
                "Task validation failed",
                task_id=task_id,
                error=str(e),
                field=e.details.get("field"),
            )
            await self.queue.fail_task(task_id, str(e), retry=False)

        except APIError as e:
            logger.error(
                "API error during task processing",
                task_id=task_id,
                error=str(e),
                status_code=e.details.get("status_code"),
            )
            await self.queue.fail_task(task_id, str(e), retry=e.is_retryable)

        except ProcessingError as e:
            logger.error(
                "Processing error during task",
                task_id=task_id,
                error=str(e),
                stage=e.details.get("stage"),
            )
            await self.queue.fail_task(task_id, str(e), retry=e.is_retryable)

        except Exception as e:
            logger.error(
                "Unexpected error during task processing",
                task_id=task_id,
                error=str(e),
            )
            await self.queue.fail_task(task_id, str(e), retry=True)

    async def _handle_task(
        self,
        task_type: str,
        params: Dict[str, Any],
        task_id: str,
    ) -> Dict[str, Any]:
        """Handle different types of generation tasks."""
        if task_type == "portrait":
            return await self._generate_portrait(params, task_id)
        elif task_type == "map":
            return await self._generate_map(params, task_id)
        elif task_type == "item":
            return await self._generate_item(params, task_id)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    @rate_limit_handler(
        window_size=60,
        max_requests=settings.MAX_CONCURRENT_GENERATIONS,
    )
    async def _generate_portrait(
        self,
        params: Dict[str, Any],
        task_id: str,
    ) -> Dict[str, Any]:
        """Generate a character portrait."""
        # Update progress
        await self.queue.update_task_progress(task_id, 10.0, "generating_base")

        # Generate base image
        prompt, neg_prompt = self.getimg._build_portrait_prompt(
            params["character"],
            params["theme"],
            params["style"],
        )
        try:
            prompt, neg_prompt = self.getimg._build_portrait_prompt(
                params["character"],
                params["theme"],
                params["style"],
            )
            image_url = await self.getimg.generate_image(
                prompt=prompt,
                negative_prompt=neg_prompt,
                size=(1024, 1024),
            )
        except Exception as e:
            raise ProcessingError(
                message="Failed to generate base portrait",
                stage="base_generation",
                details={"error": str(e)},
            )

        # Update progress
        await self.queue.update_task_progress(task_id, 50.0, "enhancing_face")

        # Enhance face details
        try:
            image_url = await self.getimg.enhance_face(image_url)
        except Exception as e:
            raise ProcessingError(
                message="Failed to enhance face",
                stage="face_enhancement",
                details={"error": str(e)},
            )

        # Update progress
        await self.queue.update_task_progress(task_id, 75.0, "applying_style")

        # Apply theme style
        try:
            image_url = await self.getimg.apply_style_transfer(
                image_url,
                params["theme"],
                params.get("style_strength", 0.75),
            )
        except Exception as e:
            raise ProcessingError(
                message="Failed to apply style",
                stage="style_transfer",
                details={"error": str(e)},
            )

        # Update progress
        await self.queue.update_task_progress(task_id, 100.0, "completed")

        return {
            "url": image_url,
            "type": "portrait",
            "theme": params["theme"],
            "character_id": params.get("character_id"),
        }

    @rate_limit_handler(
        window_size=60,
        max_requests=settings.MAX_CONCURRENT_GENERATIONS,
    )
    async def _generate_map(
        self,
        params: Dict[str, Any],
        task_id: str,
    ) -> Dict[str, Any]:
        """Generate a map."""
        # Update progress
        await self.queue.update_task_progress(task_id, 10.0, "generating_base")

        # Generate base map
        prompt, neg_prompt = self.getimg._build_map_prompt(
            params["theme"],
            params["features"],
            params["terrain"],
            params.get("is_tactical", True),
        )
        image_url = await self.getimg.generate_image(
            prompt=prompt,
            negative_prompt=neg_prompt,
            size=tuple(params.get("size", (2048, 2048))),
        )

        # Update progress
        await self.queue.update_task_progress(task_id, 75.0, "applying_style")

        # Apply theme style
        image_url = await self.getimg.apply_style_transfer(
            image_url,
            params["theme"],
            params.get("style_strength", 0.5),
        )

        # Update progress
        await self.queue.update_task_progress(task_id, 100.0, "completed")

        return {
            "url": image_url,
            "type": "map",
            "theme": params["theme"],
            "campaign_id": params.get("campaign_id"),
        }

    @rate_limit_handler(
        window_size=60,
        max_requests=settings.MAX_CONCURRENT_GENERATIONS,
    )
    async def _generate_item(
        self,
        params: Dict[str, Any],
        task_id: str,
    ) -> Dict[str, Any]:
        """Generate an item illustration."""
        # Update progress
        await self.queue.update_task_progress(task_id, 10.0, "generating_base")

        # Generate base image
        prompt, neg_prompt = self.getimg._build_item_prompt(
            params["item"],
            params["theme"],
            params["style"],
            params["properties"],
        )
        image_url = await self.getimg.generate_image(
            prompt=prompt,
            negative_prompt=neg_prompt,
            size=(1024, 1024),
        )

        # Update progress
        await self.queue.update_task_progress(task_id, 75.0, "applying_style")

        # Apply theme style
        image_url = await self.getimg.apply_style_transfer(
            image_url,
            params["theme"],
            params.get("style_strength", 0.5),
        )

        # Update progress
        await self.queue.update_task_progress(task_id, 100.0, "completed")

        return {
            "url": image_url,
            "type": "item",
            "theme": params["theme"],
            "item_id": params.get("item_id"),
        }
