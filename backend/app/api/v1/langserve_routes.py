"""LangServe routes for BMAD workflow execution.

This module provides LangServe-generated API endpoints for executing
BMAD workflows with automatic OpenAPI documentation and SSE streaming support.
"""

from typing import Dict, Any
from fastapi import FastAPI, Depends, Request
from langchain_core.runnables import RunnableConfig
from langserve import add_routes

from app.api.v1.auth import get_current_user
from app.core.langgraph.runnable_wrapper import bmad_workflow_runnable
from app.core.logging import logger
from app.models.user import User


async def inject_user_context(
    request: Request,
    config: RunnableConfig,
) -> RunnableConfig:
    """Inject user context into RunnableConfig from JWT token.

    This config modifier extracts the authenticated user from the request
    (which has already been validated by the dependencies) and injects
    the user_id into the RunnableConfig for use in the workflow execution.

    Args:
        request: FastAPI Request object containing the JWT token
        config: Original RunnableConfig from LangServe

    Returns:
        RunnableConfig: Updated config with user_id in configurable section

    Note:
        This function assumes JWT authentication has already been validated
        by the dependencies=[Depends(get_current_user)] parameter.
    """
    # Extract user from request state (set by get_current_user dependency)
    # Since dependencies are executed before per_req_config_modifier,
    # we can safely call get_current_user here
    try:
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

        security = HTTPBearer()
        credentials: HTTPAuthorizationCredentials = await security(request)

        # Re-authenticate to get user object
        # (This is safe as the token has already been validated by dependencies)
        user: User = await get_current_user(credentials)

        # Inject user_id into config
        updated_config = {
            **(config or {}),
            "configurable": {
                **((config or {}).get("configurable", {})),
                "user_id": user.id,
            },
        }

        logger.debug(
            "user_context_injected",
            user_id=user.id,
            email=user.email,
        )

        return updated_config

    except Exception as e:
        logger.error(
            "user_context_injection_failed",
            error=str(e),
        )
        # Return original config if injection fails
        # (The request will still be authenticated by dependencies)
        return config or {}


def register_langserve_routes(app: FastAPI) -> None:
    """Register LangServe routes for BMAD workflow execution.

    This function adds LangServe-generated API endpoints for the BMAD workflow,
    including automatic /invoke, /stream, /stream_events, and /playground/ endpoints.

    The following endpoints will be auto-generated:
    - POST /api/v1/bmad-workflow/invoke: Synchronous workflow execution
    - POST /api/v1/bmad-workflow/batch: Batch workflow execution
    - POST /api/v1/bmad-workflow/stream: SSE streaming workflow execution
    - POST /api/v1/bmad-workflow/stream_log: SSE with intermediate steps
    - POST /api/v1/bmad-workflow/stream_events: Structured event stream (recommended)
    - GET  /api/v1/bmad-workflow/playground/: Web UI for testing

    All endpoints require JWT authentication via Bearer token.

    Args:
        app: FastAPI application instance
    """
    try:
        add_routes(
            app,
            bmad_workflow_runnable,
            path="/api/v1/bmad-workflow",
            # Enable all endpoint types
            enable_feedback_endpoint=False,  # Disable feedback for now
            enable_public_trace_link_endpoint=False,  # Disable public tracing
            # Configure playground
            playground_type="default",  # Use default playground UI
            # Add JWT authentication dependency to all routes
            dependencies=[Depends(get_current_user)],
            # Inject user context into RunnableConfig
            per_req_config_modifier=inject_user_context,
            # Configure tags for OpenAPI documentation
            tags=["LangServe - BMAD Workflow"],
        )

        logger.info(
            "langserve_routes_registered",
            path="/api/v1/bmad-workflow",
            endpoints=["invoke", "batch", "stream", "stream_log", "stream_events", "playground"],
        )

    except Exception as e:
        logger.error(
            "langserve_routes_registration_failed",
            error=str(e),
        )
        raise
