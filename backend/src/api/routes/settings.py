"""Settings and feature flag endpoints."""

from backend.src.api import schemas
from fastapi import APIRouter
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
async def get_settings():
    """Get application settings."""
    from backend.src.infrastructure.settings_store import load_settings

    return load_settings()


@router.put("")
async def update_settings(settings: schemas.SettingsUpdate):
    """Update application settings."""
    from backend.src.infrastructure.settings_store import load_settings, save_settings

    logger.info("Updating application settings")
    current = load_settings()
    updates = settings.model_dump(exclude_none=True)
    current.update(updates)
    save_settings(current)
    logger.info("Settings updated successfully")
    return {"success": True, "message": "Impostazioni salvate"}


@router.get("/features")
async def get_features():
    """Get feature flags."""
    from backend.src.infrastructure.settings_store import load_settings

    settings = load_settings()
    return {
        "ai_enabled": settings.get("ai_enabled", True),
        "verification_enabled": False,
        "blockchain_enabled": False,
    }
