"""Main API router for the resolver service."""

from fastapi import APIRouter

from app.api.arks import router as arks_router


api_router = APIRouter()
api_router.include_router(arks_router, prefix="/arks", tags=["ARKs"])
