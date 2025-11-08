"""Runnable wrapper for BMAD workflow to enable LangServe integration.

This module provides a Runnable interface wrapper around the BMAD workflow service,
making it compatible with LangServe's automatic API generation.
"""

import asyncio
import uuid
from typing import Any, AsyncIterator, Dict, Iterator, Optional

from langchain_core.runnables import Runnable, RunnableConfig

from app.core.logging import logger
from app.services.workflow_service import workflow_service


class BMADWorkflowRunnable(Runnable):
    """Runnable wrapper for BMAD workflow execution.

    This class wraps the BMAD workflow service to make it compatible with
    LangChain's Runnable interface, enabling LangServe automatic API generation.

    The Runnable interface provides:
    - invoke(): Synchronous execution (blocking until complete)
    - ainvoke(): Asynchronous execution (blocking until complete)
    - stream(): Synchronous streaming execution
    - astream(): Asynchronous streaming execution

    Input Schema:
        {
            "problem_description": str,  # Required: Problem to solve
            "domain": str,               # Optional: Application domain
            "constraints": List[str],    # Optional: Constraint list
        }

    Output Schema:
        {
            "workflow_id": str,
            "status": str,
            "current_phase": str,
            "output_data": Dict[str, Any],
            "total_tokens": int,
            "total_cost": float,
        }
    """

    def __init__(self):
        """Initialize the BMAD workflow runnable."""
        super().__init__()
        self.workflow_service = workflow_service

    @property
    def InputType(self) -> type:
        """Return the input type for this runnable."""
        return Dict[str, Any]

    @property
    def OutputType(self) -> type:
        """Return the output type for this runnable."""
        return Dict[str, Any]

    def _extract_user_id(self, config: Optional[RunnableConfig]) -> int:
        """Extract user_id from RunnableConfig.

        LangServe will inject user_id via per_req_config_modifier.

        Args:
            config: RunnableConfig containing configurable parameters

        Returns:
            int: User ID

        Raises:
            ValueError: If user_id not found in config
        """
        if not config or "configurable" not in config:
            raise ValueError(
                "Missing user_id in config. Ensure JWT authentication is configured."
            )

        user_id = config["configurable"].get("user_id")
        if not user_id:
            raise ValueError(
                "Missing user_id in config.configurable. Check per_req_config_modifier."
            )

        return user_id

    async def ainvoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        """Asynchronously invoke the BMAD workflow (blocking until complete).

        This method creates a workflow and waits for it to complete,
        then returns the final output.

        Args:
            input: Input data containing problem_description, domain, constraints
            config: RunnableConfig containing user_id

        Returns:
            Dict containing workflow execution results

        Raises:
            ValueError: If input validation fails or user_id missing
            HTTPException: If workflow execution fails
        """
        # Extract user_id from config
        user_id = self._extract_user_id(config)

        # Extract input parameters
        problem_description = input.get("problem_description")
        if not problem_description:
            raise ValueError("problem_description is required")

        domain = input.get("domain")
        constraints = input.get("constraints", [])

        logger.info(
            "bmad_runnable_invoke_start",
            user_id=user_id,
            problem_description=problem_description[:50],
        )

        # Create workflow execution (without background task)
        workflow = await self.workflow_service.create_workflow(
            user_id=user_id,
            problem_description=problem_description,
            domain=domain,
            constraints=constraints,
            background_tasks=None,  # We'll execute synchronously
        )

        workflow_id = workflow.id

        # Execute workflow synchronously by triggering execution
        # NOTE: Since create_workflow doesn't trigger execution when background_tasks=None,
        # we need to call _execute_workflow_async directly
        await self.workflow_service._execute_workflow_async(
            workflow_id=workflow_id,
            thread_id=workflow.thread_id,
            input_data=workflow.input_data,
        )

        # Poll for completion (up to 10 minutes)
        max_wait_seconds = 600
        poll_interval = 2

        for _ in range(max_wait_seconds // poll_interval):
            workflow = await self.workflow_service.get_workflow(workflow_id)

            if workflow.status in ["completed", "failed", "cancelled", "rejected"]:
                break

            await asyncio.sleep(poll_interval)

        # Return final workflow state
        logger.info(
            "bmad_runnable_invoke_complete",
            workflow_id=str(workflow_id),
            status=workflow.status,
        )

        return {
            "workflow_id": str(workflow.id),
            "status": workflow.status,
            "current_phase": workflow.current_phase,
            "output_data": workflow.output_data or {},
            "error_message": workflow.error_message,
            "total_tokens": workflow.total_tokens,
            "total_cost": workflow.total_cost,
        }

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        """Synchronously invoke the BMAD workflow (blocking until complete).

        This is a synchronous wrapper around ainvoke().

        Args:
            input: Input data containing problem_description, domain, constraints
            config: RunnableConfig containing user_id

        Returns:
            Dict containing workflow execution results
        """
        # Run async method in sync context
        return asyncio.run(self.ainvoke(input, config))

    async def astream(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Asynchronously stream the BMAD workflow execution events.

        This method creates a workflow and streams execution events in real-time,
        including phase changes, agent outputs, and HITL interrupts.

        Args:
            input: Input data containing problem_description, domain, constraints
            config: RunnableConfig containing user_id

        Yields:
            Dict: Workflow execution events

        Raises:
            ValueError: If input validation fails or user_id missing
            HTTPException: If workflow execution fails
        """
        # Extract user_id from config
        user_id = self._extract_user_id(config)

        # Extract input parameters
        problem_description = input.get("problem_description")
        if not problem_description:
            raise ValueError("problem_description is required")

        domain = input.get("domain")
        constraints = input.get("constraints", [])

        logger.info(
            "bmad_runnable_stream_start",
            user_id=user_id,
            problem_description=problem_description[:50],
        )

        # Create workflow execution with background task execution
        workflow = await self.workflow_service.create_workflow(
            user_id=user_id,
            problem_description=problem_description,
            domain=domain,
            constraints=constraints,
            background_tasks=None,  # We'll execute in parallel with streaming
        )

        workflow_id = workflow.id

        # Start workflow execution in background
        execution_task = asyncio.create_task(
            self.workflow_service._execute_workflow_async(
                workflow_id=workflow_id,
                thread_id=workflow.thread_id,
                input_data=workflow.input_data,
            )
        )

        # Stream workflow events
        try:
            async for event in self.workflow_service.stream_workflow(workflow_id):
                # Yield event in LangServe-compatible format
                yield {
                    "event": event.get("event_type", "unknown"),
                    "data": event.get("data", {}),
                    "timestamp": event.get("timestamp"),
                }

                # Break if workflow completed/failed
                if event.get("event_type") in ["workflow_complete", "workflow_failed"]:
                    break

        except Exception as e:
            logger.error(
                "bmad_runnable_stream_error",
                error=str(e),
                workflow_id=str(workflow_id),
            )
            # Send error event
            yield {
                "event": "error",
                "data": {"error": str(e)},
                "timestamp": None,
            }
        finally:
            # Ensure execution task is cleaned up
            if not execution_task.done():
                execution_task.cancel()
                try:
                    await execution_task
                except asyncio.CancelledError:
                    pass

        logger.info("bmad_runnable_stream_complete", workflow_id=str(workflow_id))

    def stream(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Synchronously stream the BMAD workflow execution events.

        This is a synchronous wrapper around astream().

        Args:
            input: Input data containing problem_description, domain, constraints
            config: RunnableConfig containing user_id

        Yields:
            Dict: Workflow execution events
        """
        # Create async generator
        async_gen = self.astream(input, config)

        # Run async generator in sync context using asyncio.run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            while True:
                try:
                    event = loop.run_until_complete(async_gen.__anext__())
                    yield event
                except StopAsyncIteration:
                    break
        finally:
            loop.close()


# Create singleton instance for LangServe registration
bmad_workflow_runnable = BMADWorkflowRunnable()
