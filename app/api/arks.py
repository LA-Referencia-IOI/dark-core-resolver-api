"""Public ARK resolution endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import get_settings
from app.dependencies import get_corelib_client, get_metadata_storage
from app.services.resolver_service import ResolverService


router = APIRouter()


def get_resolver_service() -> ResolverService:
    """Build a resolver service from shared dependencies."""
    settings = get_settings()
    return ResolverService(
        corelib_client=get_corelib_client(),
        metadata_storage=get_metadata_storage(),
        redirect_status=settings.resolver_redirect_status,
    )


@router.api_route(
    "/{ark:path}",
    methods=["GET", "HEAD"],
    summary="Resolve an ARK",
    description="Redirects to the target by default, or serves ?info / ?metadata views.",
)
async def resolve_ark(
    request: Request,
    ark: str,
    service: ResolverService = Depends(get_resolver_service),
):
    """Resolve an ARK to its default target or metadata views."""
    has_info = "info" in request.query_params
    has_metadata = "metadata" in request.query_params

    if has_info and has_metadata:
        raise HTTPException(status_code=400, detail="Use either ?info or ?metadata, not both")

    if has_info:
        return service.build_public_info(ark)
    if has_metadata:
        return service.build_metadata_response(ark)
    return service.redirect_to_target(ark)
