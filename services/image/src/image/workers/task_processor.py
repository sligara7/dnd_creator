"""Async worker for processing generation tasks."""
import asyncio
import logging
from dataclasses import dataclass
import psutil
from typing import Callable, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from image.core.getimg import GetImgClient
from image.core.metrics import record_memory_usage, record_worker_count
from image.models.generation import TaskType
from image.services.queue import QueueService

logger = logging.getLogger(__name__)


@dataclass
class WorkerConfig:
    """Configuration for task worker."""
    polling_interval: float = 1.0  # Time between queue checks in seconds
    max_concurrent_tasks: int = 3  # Maximum number of concurrent tasks
    cleanup_interval: float = 3600  # Run cleanup every hour
    cleanup_max_age: int = 24  # Consider tasks stale after 24 hours


class TaskProcessor:
    """Worker for processing image generation tasks."""

    def __init__(
        self,
        queue_service: QueueService,
        getimg_client: GetImgClient,
        config: Optional[WorkerConfig] = None
    ) -> None:
        """Initialize the task processor.

        Args:
            queue_service: Queue service for task management
            getimg_client: GetImg.AI API client
            config: Optional worker configuration
        """
        self.queue = queue_service
        self.getimg = getimg_client
        self.config = config or WorkerConfig()

        # Track running tasks
        self.running_tasks: Dict[str, asyncio.Task] = {}

        # Register task handlers
        self.handlers = {
            TaskType.CHARACTER_PORTRAIT: self._handle_portrait,
            TaskType.MAP: self._handle_map,
            TaskType.ITEM: self._handle_item,
            TaskType.OVERLAY: self._handle_overlay,
            TaskType.ENHANCEMENT: self._handle_enhancement,
        }

        # Control flag
        self.running = False

    async def start(self) -> None:
        """Start the task processor."""
        if self.running:
            return

        self.running = True
        asyncio.create_task(self._cleanup_loop())
        asyncio.create_task(self._metrics_loop())
        await self._process_loop()

    async def stop(self) -> None:
        """Stop the task processor."""
        self.running = False

        # Cancel all running tasks
        for task in self.running_tasks.values():
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        self.running_tasks.clear()

    async def _process_loop(self) -> None:
        """Main processing loop."""
        while self.running:
            try:
                # Check if we can process more tasks
                if len(self.running_tasks) >= self.config.max_concurrent_tasks:
                    await asyncio.sleep(self.config.polling_interval)
                    continue

                # Clean up completed tasks
                done_tasks = [
                    task_id for task_id, task in self.running_tasks.items()
                    if task.done()
                ]
                for task_id in done_tasks:
                    self.running_tasks.pop(task_id)

                # Get next task from queue
                task = await self.queue.dequeue_task()
                if not task:
                    await asyncio.sleep(self.config.polling_interval)
                    continue

                # Start task processing
                logger.info(f"Starting task {task.id} of type {task.type}")
                handler = self.handlers.get(task.type)
                if not handler:
                    await self.queue.fail_task(
                        task.id,
                        f"No handler for task type: {task.type}",
                        retry=False
                    )
                    continue

                # Create and track task
                process_task = asyncio.create_task(
                    self._process_task(task.id, handler)
                )
                self.running_tasks[str(task.id)] = process_task

            except Exception as e:
                logger.exception("Error in processing loop")
                await asyncio.sleep(self.config.polling_interval)

    async def _process_task(
        self,
        task_id: str,
        handler: Callable
    ) -> None:
        """Process a single task.

        Args:
            task_id: ID of task to process
            handler: Handler function for the task type
        """
        try:
            await handler(task_id)
        except asyncio.CancelledError:
            # Task was cancelled, mark as failed
            await self.queue.fail_task(
                task_id,
                "Task cancelled",
                retry=True
            )
        except Exception as e:
            # Task failed, mark for retry
            logger.exception(f"Error processing task {task_id}")
            await self.queue.fail_task(
                task_id,
                str(e),
                retry=True
            )

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of stale tasks."""
        while self.running:
            try:
                # Run cleanup
                cleaned = await self.queue.cleanup_stale_tasks(
                    max_age_hours=self.config.cleanup_max_age
                )
                if cleaned:
                    logger.info(f"Cleaned up {cleaned} stale tasks")

                # Wait for next cleanup interval
                await asyncio.sleep(self.config.cleanup_interval)

            except Exception as e:
                logger.exception("Error in cleanup loop")
                await asyncio.sleep(self.config.cleanup_interval)

    async def _metrics_loop(self) -> None:
        """Periodic update of worker metrics."""
        while self.running:
            try:
                # Record worker count
                active_workers = len([t for t in self.running_tasks.values() if not t.done()])
                record_worker_count(active_workers)

                # Record memory usage
                process = psutil.Process()
                memory_info = process.memory_info()
                record_memory_usage("worker", memory_info.rss)

                # Wait before next update
                await asyncio.sleep(15)  # Update every 15 seconds

            except Exception as e:
                logger.exception("Error in metrics loop")
                await asyncio.sleep(15)

    # Task type handlers
    async def _handle_portrait(self, task_id: str) -> None:
        """Handle character portrait generation.

        Args:
            task_id: ID of task to process
        """
        # Update progress
        await self.queue.update_progress(
            task_id,
            10,
            "Generating character portrait..."
        )

        # Get task details
        task = await self.queue.task_repo.get_by_id(task_id)
        if not task:
            return

        try:
            # Generate portrait
            result = await self.getimg.generate_portrait(
                task.parameters["prompt"],
                task.parameters.get("style", "realistic"),
                task.parameters.get("width", 512),
                task.parameters.get("height", 512),
                task.parameters.get("num_steps", 30),
                task.parameters.get("guidance_scale", 7.5),
                progress_callback=lambda p: self.queue.update_progress(
                    task_id,
                    10 + (p * 0.8),  # Scale from 10-90%
                    "Generating portrait..."
                )
            )

            # Post-process if needed
            if task.parameters.get("enhance_face", False):
                await self.queue.update_progress(
                    task_id,
                    90,
                    "Enhancing portrait..."
                )
                result = await self.getimg.enhance_face(result)

            # Store result
            await self.queue.complete_task(task_id, {"image_data": result})

        except Exception as e:
            raise Exception(f"Portrait generation failed: {str(e)}")

    async def _handle_map(self, task_id: str) -> None:
        """Handle map generation.

        Args:
            task_id: ID of task to process
        """
        # Update progress
        await self.queue.update_progress(
            task_id,
            10,
            "Generating map..."
        )

        # Get task details
        task = await self.queue.task_repo.get_by_id(task_id)
        if not task:
            return

        try:
            # Generate map
            result = await self.getimg.generate_map(
                task.parameters["prompt"],
                task.parameters.get("style", "fantasy"),
                task.parameters.get("width", 1024),
                task.parameters.get("height", 1024),
                task.parameters.get("num_steps", 50),
                task.parameters.get("guidance_scale", 7.5),
                progress_callback=lambda p: self.queue.update_progress(
                    task_id,
                    10 + (p * 0.8),  # Scale from 10-90%
                    "Generating map..."
                )
            )

            # Post-process
            if task.parameters.get("add_grid", False):
                await self.queue.update_progress(
                    task_id,
                    90,
                    "Adding grid overlay..."
                )
                result = await self.getimg.add_grid(
                    result,
                    task.parameters.get("grid_size", 32)
                )

            # Store result
            await self.queue.complete_task(task_id, {"image_data": result})

        except Exception as e:
            raise Exception(f"Map generation failed: {str(e)}")

    async def _handle_item(self, task_id: str) -> None:
        """Handle item visualization generation.

        Args:
            task_id: ID of task to process
        """
        # Update progress
        await self.queue.update_progress(
            task_id,
            10,
            "Generating item visualization..."
        )

        # Get task details
        task = await self.queue.task_repo.get_by_id(task_id)
        if not task:
            return

        try:
            # Generate item image
            result = await self.getimg.generate_item(
                task.parameters["prompt"],
                task.parameters.get("style", "fantasy"),
                task.parameters.get("width", 512),
                task.parameters.get("height", 512),
                task.parameters.get("num_steps", 30),
                task.parameters.get("guidance_scale", 7.5),
                progress_callback=lambda p: self.queue.update_progress(
                    task_id,
                    10 + (p * 0.8),  # Scale from 10-90%
                    "Generating item..."
                )
            )

            # Store result
            await self.queue.complete_task(task_id, {"image_data": result})

        except Exception as e:
            raise Exception(f"Item generation failed: {str(e)}")

    async def _handle_overlay(self, task_id: str) -> None:
        """Handle tactical overlay generation.

        Args:
            task_id: ID of task to process
        """
        # Update progress
        await self.queue.update_progress(
            task_id,
            10,
            "Applying overlay..."
        )

        # Get task details
        task = await self.queue.task_repo.get_by_id(task_id)
        if not task:
            return

        try:
            # Generate overlay
            base_image = task.parameters["base_image"]
            overlay_type = task.parameters["overlay_type"]
            overlay_params = task.parameters.get("overlay_params", {})

            result = await self.getimg.apply_overlay(
                base_image,
                overlay_type,
                **overlay_params
            )

            # Store result
            await self.queue.complete_task(task_id, {"image_data": result})

        except Exception as e:
            raise Exception(f"Overlay application failed: {str(e)}")

    async def _handle_enhancement(self, task_id: str) -> None:
        """Handle image enhancement tasks.

        Args:
            task_id: ID of task to process
        """
        # Update progress
        await self.queue.update_progress(
            task_id,
            10,
            "Enhancing image..."
        )

        # Get task details
        task = await self.queue.task_repo.get_by_id(task_id)
        if not task:
            return

        try:
            base_image = task.parameters["image"]
            enhancement_type = task.parameters["enhancement_type"]
            enhancement_params = task.parameters.get("enhancement_params", {})

            # Apply enhancement
            result = await self.getimg.enhance_image(
                base_image,
                enhancement_type,
                **enhancement_params,
                progress_callback=lambda p: self.queue.update_progress(
                    task_id,
                    10 + (p * 0.8),  # Scale from 10-90%
                    "Enhancing image..."
                )
            )

            # Store result
            await self.queue.complete_task(task_id, {"image_data": result})

        except Exception as e:
            raise Exception(f"Image enhancement failed: {str(e)}")
