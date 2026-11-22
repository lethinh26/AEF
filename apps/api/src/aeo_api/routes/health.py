from aeo_platform.config import get_settings
from aeo_platform.db import database_is_ready
from fastapi import APIRouter, Response, status

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok", "service": "aeo-api"}


@router.get("/health/ready")
async def readiness(response: Response) -> dict[str, str]:
    if not await database_is_ready():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "dependency": "postgresql"}
    return {"status": "ready", "environment": get_settings().environment}
