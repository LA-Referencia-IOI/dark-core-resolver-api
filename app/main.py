"""dARK Core Resolver API entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.dependencies import (
    get_corelib_client,
    get_metadata_storage,
    init_corelib_client,
    init_metadata_storage,
    shutdown_corelib_client,
    shutdown_metadata_storage,
)
from app.exceptions.handlers import register_exception_handlers


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize long-lived dependencies during app startup."""
    logger.info("Starting dARK Core Resolver API...")
    init_corelib_client()
    app.state.metadata_storage = init_metadata_storage()
    yield
    logger.info("Shutting down dARK Core Resolver API...")
    shutdown_metadata_storage()
    shutdown_corelib_client()


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(
        title="dARK Core Resolver API",
        description="Read-only ARK resolver backed by blockchain and shared metadata storage.",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health/live", tags=["Health"])
    async def liveness_check():
        """Cheap process liveness check; does not call RPC or storage."""
        return {"status": "alive"}

    @app.get("/health", tags=["Health"])
    async def health_check():
        settings = get_settings()
        response = {"status": "healthy", "storage_type": settings.metadata_storage_type}

        try:
            client = get_corelib_client()
            response["blockchain_connected"] = client.is_connected()
            response["current_block"] = client.get_block_number()
        except Exception as exc:
            response["status"] = "degraded"
            response["blockchain_connected"] = False
            response["blockchain_error"] = str(exc)

        try:
            storage = get_metadata_storage()
            response["metadata_storage"] = "healthy" if storage.health_check() else "unhealthy"
            if response["metadata_storage"] != "healthy" and response["status"] == "healthy":
                response["status"] = "degraded"
        except Exception as exc:
            response["metadata_storage"] = "unhealthy"
            response["metadata_storage_error"] = str(exc)
            if response["status"] == "healthy":
                response["status"] = "degraded"

        return response

    return app


app = create_app()


def run_server():
    """Run the server from the package entrypoint."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.resolver_api_host,
        port=settings.resolver_api_port,
        reload=False,
    )
