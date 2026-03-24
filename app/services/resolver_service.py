"""Core resolution service for redirect, info, and metadata flows."""

from fastapi import HTTPException, Response
from fastapi.responses import RedirectResponse

from dark_core_lib import DARKCoreClient, parse_ark_id
from dark_core_lib.exceptions import ARKError, ARKNotFoundError
from dark_core_lib.metadata import (
    Level1Metadata,
    MetadataNotFoundError,
    MetadataService,
    MetadataStorage,
    StorageError,
)

from app.models.public import AlternateIdentifierResponse, ArkInfoResponse


class ResolverService:
    """Resolve ARKs from blockchain plus shared metadata storage."""

    def __init__(
        self,
        corelib_client: DARKCoreClient,
        metadata_storage: MetadataStorage,
        redirect_status: int = 302,
    ):
        self.corelib_client = corelib_client
        self.metadata_service = MetadataService(metadata_storage)
        self.redirect_status = redirect_status

    def _get_ark_info(self, raw_ark: str):
        try:
            parsed = parse_ark_id(raw_ark)
        except ARKError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        try:
            info = self.corelib_client.get_ark(parsed.naan, parsed.name)
        except ARKNotFoundError as exc:
            raise HTTPException(status_code=404, detail=f"ARK not found: {parsed.canonical}") from exc
        except ARKError as exc:
            raise HTTPException(status_code=502, detail=f"Blockchain resolution failed: {exc}") from exc

        return parsed, info

    def _get_level1_metadata(self, level1_cid: str) -> Level1Metadata:
        if not level1_cid:
            raise HTTPException(status_code=502, detail="Published metadata is missing")

        try:
            return self.metadata_service.load_level1(level1_cid)
        except MetadataNotFoundError as exc:
            raise HTTPException(status_code=502, detail="Published metadata not found in storage") from exc
        except StorageError as exc:
            raise HTTPException(status_code=502, detail=f"Metadata backend unavailable: {exc}") from exc
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=f"Invalid Level-1 metadata payload: {exc}") from exc

    def redirect_to_target(self, raw_ark: str) -> RedirectResponse:
        _, info = self._get_ark_info(raw_ark)
        return RedirectResponse(url=info.url, status_code=self.redirect_status)

    def build_public_info(self, raw_ark: str) -> ArkInfoResponse:
        _, info = self._get_ark_info(raw_ark)
        level1 = self._get_level1_metadata(info.cid)

        alternate_identifiers = None
        if level1.alternate_identifiers:
            alternate_identifiers = [
                AlternateIdentifierResponse(schema=item.schema_, value=item.value)
                for item in level1.alternate_identifiers
            ]

        return ArkInfoResponse(
            ark=info.ark_id,
            target=info.url,
            created_at=info.created_at,
            updated_at=info.updated_at,
            metadata_schema=level1.original_metadata.schema_,
            title=level1.title,
            authors=level1.authors,
            year=level1.year,
            publisher=level1.publisher,
            resource_type=level1.resource_type,
            language=level1.language,
            abstract=level1.abstract,
            subjects=level1.subjects,
            rights=level1.rights,
            alternate_identifiers=alternate_identifiers,
            alternate_urls=level1.alternate_urls,
        )

    def build_metadata_response(self, raw_ark: str) -> Response:
        _, info = self._get_ark_info(raw_ark)
        level1 = self._get_level1_metadata(info.cid)

        level2_cid = level1.original_metadata.cid
        if not level2_cid:
            raise HTTPException(status_code=404, detail="Original metadata is not available")

        try:
            document = self.metadata_service.load_level2(level1)
        except MetadataNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Original metadata not found in storage") from exc
        except StorageError as exc:
            raise HTTPException(status_code=502, detail=f"Metadata backend unavailable: {exc}") from exc

        return Response(content=document.content, media_type=document.content_type)
