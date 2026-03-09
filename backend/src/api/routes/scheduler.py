"""Background scheduler endpoints."""

from backend.src.api import state
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


@router.get("/status")
async def get_scheduler_status():
    """Get background scheduler status."""
    if state.scheduler is None:
        return {"running": False, "jobs": []}
    return state.scheduler.get_status()


@router.post("/trigger")
async def trigger_poll():
    """Manually trigger feed polling."""
    if state.scheduler is None:
        raise HTTPException(status_code=503, detail="Scheduler not running")
    state.scheduler.trigger_poll_now()
    return {"success": True, "message": "Feed polling triggered"}
