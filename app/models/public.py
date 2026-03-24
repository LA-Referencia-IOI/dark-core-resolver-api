"""Public response models for the resolver API."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AlternateIdentifierResponse(BaseModel):
    """Public alternate identifier projection."""

    schema_: str = Field(..., alias="schema", description="Identifier schema")
    value: str = Field(..., description="Identifier value")

    model_config = {"populate_by_name": True}


class ArkInfoResponse(BaseModel):
    """Public `?info` response."""

    ark: str
    target: str
    created_at: datetime
    updated_at: datetime
    metadata_schema: Optional[str] = None

    title: str
    authors: list[str]
    year: int
    publisher: Optional[str] = None
    resource_type: Optional[str] = None
    language: Optional[str] = None
    abstract: Optional[str] = None
    subjects: Optional[List[str]] = None
    rights: Optional[str] = None
    alternate_identifiers: Optional[List[AlternateIdentifierResponse]] = None
    alternate_urls: Optional[List[str]] = None
