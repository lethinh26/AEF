from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aeo_platform.config import get_settings
from aeo_platform.logging import configure_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aeo_api.routes.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="AEO API",
        summary="Control and intelligence API for the Autonomous Engineering Organization.",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "If-Match"],
    )
    application.include_router(health_router)
    return application


app = create_app()
