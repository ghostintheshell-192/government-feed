"""Cache status endpoints."""

from backend.src.api import state
from fastapi import APIRouter

router = APIRouter(prefix="/api/cache", tags=["cache"])


@router.get("/status")
async def get_cache_status():
    """Get Redis cache status."""
    if state.cache is None:
        return {"available": False, "message": "Cache not initialized"}
    return {
        "available": state.cache.is_available(),
        "message": "Cache is operational" if state.cache.is_available() else "Cache is unavailable",
    }
