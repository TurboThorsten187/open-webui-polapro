# backend/open_webui/routers/polapro.py
"""
PoLaPro Data Pipeline Admin Router.

Provides admin-only proxy endpoints for the host-side pipeline agent,
and a maintenance mode middleware that blocks user queries during
pipeline runs while keeping the admin panel accessible.

This is a custom PoLaPro addition — completely isolated from upstream
Open WebUI code to avoid merge conflicts on updates.
"""

import asyncio
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from open_webui.utils.auth import get_admin_user

log = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The host-side pipeline agent runs on localhost:8001.
# Docker containers reach the host via host.docker.internal.
PIPELINE_AGENT_URL = "http://host.docker.internal:8001"

# Paths that are ALWAYS allowed through, even during maintenance.
# This ensures admins can still log in, access the admin panel,
# manage the pipeline, and load the Svelte frontend.
MAINTENANCE_ALLOWED_PREFIXES = (
    "/api/v1/polapro",      # Pipeline admin endpoints
    "/api/v1/configs",       # Admin settings
    "/api/v1/auths",         # Login/auth (so admins can log back in)
    "/api/v1/users",         # User profile endpoints
    "/admin",                # Admin panel pages
    "/static",               # Static files
    "/health",               # Health check
    "/_app",                 # SvelteKit internal assets
    "/favicon",              # Favicon
    "/manifest",             # PWA manifest
)

# Paths that are BLOCKED during maintenance (user-facing query endpoints).
MAINTENANCE_BLOCKED_PREFIXES = (
    "/api/v1/chats",
    "/api/v1/retrieval",
    "/openai",
    "/ollama",
    "/api/chat",
    "/api/v1/chat",
    "/api/embeddings",
    "/api/v1/embeddings",
    "/api/message",
    "/api/v1/messages",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------


class PipelineTriggerRequest(BaseModel):
    pipeline: str  # "speech" or "manifesto"
    shutdown_rag: bool = True
    terms: list[int] = [21]
    use_gpu: bool = False
    export_excel: bool = False
    keep_older_data: bool = True
    keep_newer_data: bool = True


# ---------------------------------------------------------------------------
# Helper: Proxy to host agent
# ---------------------------------------------------------------------------


async def _proxy_get(path: str, timeout: float = 10.0) -> dict:
    """Proxy a GET request to the pipeline agent."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{PIPELINE_AGENT_URL}{path}")
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        raise HTTPException(503, detail="Pipeline agent is not reachable. Is the pipeline-agent.service running?")
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, detail=e.response.text)
    except Exception as e:
        log.error("Error proxying GET %s: %s", path, e)
        raise HTTPException(502, detail=f"Error communicating with pipeline agent: {e}")


async def _proxy_post(path: str, data: dict | None = None, timeout: float = 30.0) -> dict:
    """Proxy a POST request to the pipeline agent."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{PIPELINE_AGENT_URL}{path}", json=data or {})
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        raise HTTPException(503, detail="Pipeline agent is not reachable. Is the pipeline-agent.service running?")
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, detail=e.response.text)
    except Exception as e:
        log.error("Error proxying POST %s: %s", path, e)
        raise HTTPException(502, detail=f"Error communicating with pipeline agent: {e}")


# ---------------------------------------------------------------------------
# Endpoints: Pipeline Management (all admin-only)
# ---------------------------------------------------------------------------


@router.get("/pipeline/status")
async def get_pipeline_status(user=Depends(get_admin_user)):
    """Get the current pipeline status from the host agent."""
    return await _proxy_get("/api/v1/pipeline/status")


@router.post("/pipeline/trigger")
async def trigger_pipeline(req: PipelineTriggerRequest, user=Depends(get_admin_user)):
    """Trigger a data generation pipeline run via the host agent."""
    return await _proxy_post("/api/v1/pipeline/trigger", req.model_dump())


@router.post("/pipeline/cancel")
async def cancel_pipeline(user=Depends(get_admin_user)):
    """Cancel the currently running pipeline."""
    return await _proxy_post("/api/v1/pipeline/cancel")


@router.get("/pipeline/logs/stream")
async def stream_pipeline_logs(
    request: Request,
    from_line: int = Query(0, ge=0),
    user=Depends(get_admin_user),
):
    """
    Stream pipeline logs via Server-Sent Events.
    Proxies the SSE stream from the host agent.
    """
    async def event_proxy():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "GET",
                    f"{PIPELINE_AGENT_URL}/api/v1/pipeline/logs/stream?from_line={from_line}",
                ) as resp:
                    async for line in resp.aiter_lines():
                        # Check if client disconnected
                        if await request.is_disconnected():
                            break
                        if line:
                            yield f"{line}\n\n"
        except httpx.ConnectError:
            yield 'data: {"type": "error", "message": "Pipeline agent is not reachable."}\n\n'
        except Exception as e:
            log.error("Error streaming logs: %s", e)
            yield f'data: {{"type": "error", "message": "{str(e)}"}}\n\n'

    return StreamingResponse(
        event_proxy(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/pipeline/runs/{pipeline_type}")
async def get_pipeline_runs(pipeline_type: str, user=Depends(get_admin_user)):
    """Get run history for a pipeline type."""
    return await _proxy_get(f"/api/v1/pipeline/runs/{pipeline_type}")


@router.get("/pipeline/runs/{pipeline_type}/{run_id}/log")
async def get_pipeline_run_log(pipeline_type: str, run_id: int, user=Depends(get_admin_user)):
    """Get the log file contents for a specific run."""
    return await _proxy_get(f"/api/v1/pipeline/runs/{pipeline_type}/{run_id}/log", timeout=30.0)


# ---------------------------------------------------------------------------
# Endpoint: Maintenance Status
# ---------------------------------------------------------------------------


@router.get("/maintenance/status")
async def get_maintenance_status(request: Request):
    """
    Check if maintenance mode is active.
    This endpoint is accessible to all users (no admin requirement)
    so the frontend can check and display the maintenance banner.
    """
    is_maintenance = getattr(request.app.state, "POLAPRO_MAINTENANCE_MODE", False)
    return {"maintenance": is_maintenance}


@router.get("/disclaimer")
async def get_disclaimer():
    """
    Get the Datenschutzdisclaimer text content.
    Accessible without authentication for the registration flow.
    """
    import os
    disclaimer_path = os.path.join(os.path.dirname(__file__), "..", "Datenschutzdisclaimer.md")
    if os.path.exists(disclaimer_path):
        try:
            with open(disclaimer_path, "r", encoding="utf-8") as f:
                return {"content": f.read()}
        except Exception as e:
            log.error(f"Error reading Datenschutzdisclaimer file: {e}")
            return {"content": ""}
    else:
        log.warning(f"Datenschutzdisclaimer file not found at {disclaimer_path}")
        return {"content": ""}


# ---------------------------------------------------------------------------
# Maintenance Mode Middleware
# ---------------------------------------------------------------------------


class PolaProMaintenanceMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that blocks user-facing query endpoints during
    pipeline maintenance, while allowing admin panel access.

    The middleware syncs its state from the host agent's /status endpoint
    via a background polling task started on first request.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Check if maintenance mode is active
        is_maintenance = getattr(request.app.state, "POLAPRO_MAINTENANCE_MODE", False)

        if is_maintenance:
            # Always allow specific paths through
            if any(path.startswith(prefix) for prefix in MAINTENANCE_ALLOWED_PREFIXES):
                return await call_next(request)

            # Block user-facing endpoints
            if any(path.startswith(prefix) for prefix in MAINTENANCE_BLOCKED_PREFIXES):
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": "Unser System wird gerade gewartet. Bitte versuchen Sie es später erneut."
                    },
                )

            # WebSocket connections should also be blocked during maintenance
            if "/ws/" in path:
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": "Unser System wird gerade gewartet. Bitte versuchen Sie es später erneut."
                    },
                )

        return await call_next(request)


# ---------------------------------------------------------------------------
# Background Task: Sync maintenance state from host agent
# ---------------------------------------------------------------------------

_sync_task: Optional[asyncio.Task] = None


async def _sync_maintenance_state(app):
    """
    Periodically poll the host agent's /status endpoint to determine
    whether maintenance mode should be active.

    Maintenance mode is active when the agent reports status == 'running'.
    """
    while True:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{PIPELINE_AGENT_URL}/api/v1/pipeline/status")
                if resp.status_code == 200:
                    data = resp.json()
                    # Maintenance is active when a pipeline is running
                    app.state.POLAPRO_MAINTENANCE_MODE = data.get("status") == "running"
                else:
                    # Agent is reachable but returned error — assume not in maintenance
                    app.state.POLAPRO_MAINTENANCE_MODE = False
        except httpx.ConnectError:
            # Agent is not reachable — assume not in maintenance (agent may be down)
            app.state.POLAPRO_MAINTENANCE_MODE = False
        except Exception as e:
            log.debug("Error syncing maintenance state: %s", e)

        await asyncio.sleep(15)  # Poll every 15 seconds


def start_maintenance_sync(app):
    """Start the background maintenance state sync task."""
    global _sync_task
    if _sync_task is None or _sync_task.done():
        _sync_task = asyncio.create_task(_sync_maintenance_state(app))
        log.info("PoLaPro maintenance state sync started (polling every 15s).")
