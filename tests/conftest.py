"""Pytest fixtures for dARK Core Resolver API."""

import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


_COMPONENTS_ROOT = Path(__file__).resolve().parents[3]
_CORE_LIB_ROOT = _COMPONENTS_ROOT / "libraries" / "dark-core-lib"
if str(_CORE_LIB_ROOT) not in sys.path:
    sys.path.insert(0, str(_CORE_LIB_ROOT))


from dark_core_lib.metadata import StoredDocument  # noqa: E402
from dark_core_lib.models import ARKInfo  # noqa: E402

from app.main import app  # noqa: E402
import app.dependencies as dependencies_module  # noqa: E402
from app.api.arks import get_resolver_service  # noqa: E402
from app.dependencies import get_corelib_client, get_metadata_storage  # noqa: E402


@pytest.fixture
def mock_corelib():
    """Mock blockchain client."""
    mock = MagicMock()
    mock.is_connected.return_value = True
    mock.get_block_number.return_value = 4242
    mock.get_ark.return_value = ARKInfo(
        naan="12345",
        name="test001",
        url="https://example.org/object/1",
        cid="internal-level1-cid",
        owner="0x1234567890123456789012345678901234567890",
        created_at=datetime(2026, 1, 21, 12, 0, 0),
        updated_at=datetime(2026, 1, 21, 13, 0, 0),
    )
    return mock


@pytest.fixture
def level1_payload():
    """Canonical Level-1 payload used in resolver tests."""
    return {
        "$schema": "https://dark.la-referencia.info/schemas/ark-metadata/v1",
        "schema_version": "1.0",
        "ark": "ark:/12345/test001",
        "title": "Test Resource",
        "authors": ["Doe, Jane"],
        "year": 2025,
        "publisher": "Test Publisher",
        "resource_type": "dataset",
        "language": "en",
        "abstract": "Resolver test payload",
        "subjects": ["testing", "resolver"],
        "rights": "CC-BY",
        "alternate_identifiers": [{"schema": "doi", "value": "10.1234/demo"}],
        "alternate_urls": ["https://example.org/alt/1"],
        "original_metadata": {
            "schema": "oai_dc",
            "media_type": "application/xml",
            "cid": "internal-level2-cid",
        },
    }


@pytest.fixture
def mock_storage(level1_payload):
    """Mock metadata storage backend."""
    mock = MagicMock()
    mock.health_check.return_value = True

    documents = {
        "internal-level1-cid": StoredDocument(
            content=json.dumps(level1_payload).encode("utf-8"),
            content_type="application/json",
        ),
        "internal-level2-cid": StoredDocument(
            content=b"<record><title>Test Resource</title></record>",
            content_type="application/octet-stream",
        ),
    }

    def _get_document(cid: str):
        if cid not in documents:
            raise KeyError(cid)
        return documents[cid]

    mock.get_document.side_effect = _get_document
    return mock


@pytest.fixture
def client(mock_corelib, mock_storage):
    """Create a test client with mocked dependencies."""
    app.dependency_overrides[get_corelib_client] = lambda: mock_corelib
    app.dependency_overrides[get_metadata_storage] = lambda: mock_storage
    app.dependency_overrides[get_resolver_service] = lambda: get_resolver_service()
    dependencies_module._corelib_client = mock_corelib
    dependencies_module._metadata_storage = mock_storage

    with patch("app.main.init_corelib_client", return_value=mock_corelib):
        with patch("app.main.init_metadata_storage", return_value=mock_storage):
            with TestClient(app) as test_client:
                yield test_client

    app.dependency_overrides.clear()
    dependencies_module._corelib_client = None
    dependencies_module._metadata_storage = None
