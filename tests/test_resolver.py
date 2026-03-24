"""Tests for dARK Core Resolver API."""

from unittest.mock import MagicMock

from dark_core_lib.exceptions import ARKNotFoundError
from dark_core_lib.metadata import MetadataNotFoundError, StoredDocument


def test_get_ark_redirects_to_target(client):
    response = client.get("/api/v1/arks/ark:/12345/test001", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "https://example.org/object/1"


def test_get_ark_info_returns_l1_without_cids(client):
    response = client.get("/api/v1/arks/ark:/12345/test001?info")

    assert response.status_code == 200
    data = response.json()
    assert data["ark"] == "ark:/12345/test001"
    assert data["title"] == "Test Resource"
    assert data["metadata_schema"] == "dublin_core"
    payload = response.text
    assert "internal-level1-cid" not in payload
    assert "internal-level2-cid" not in payload


def test_get_ark_metadata_returns_l2_raw(client):
    response = client.get("/api/v1/arks/ark:/12345/test001?metadata")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert response.text == "<record><title>Test Resource</title></record>"


def test_get_ark_metadata_can_return_json(client, mock_storage):
    mock_storage.get_document.side_effect = [
        StoredDocument(
            content=(
                b'{"$schema":"x","schema_version":"1.0","title":"A","authors":["B"],'
                b'"year":2024,"original_metadata":{"schema":"datacite","cid":"internal-level2-json"}}'
            ),
            content_type="application/json",
        ),
        StoredDocument(
            content=b'{"identifier":"10.1234/demo"}',
            content_type="application/json",
        ),
    ]

    response = client.get("/api/v1/arks/ark:/12345/test001?metadata")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"identifier": "10.1234/demo"}


def test_get_ark_rejects_info_and_metadata_together(client):
    response = client.get("/api/v1/arks/ark:/12345/test001?info&metadata")

    assert response.status_code == 400


def test_get_ark_returns_404_when_missing(client, mock_corelib):
    mock_corelib.get_ark.side_effect = ARKNotFoundError("missing")

    response = client.get("/api/v1/arks/ark:/12345/missing", follow_redirects=False)

    assert response.status_code == 404


def test_get_ark_info_returns_502_when_published_l1_missing(client, mock_storage):
    mock_storage.get_document.side_effect = MetadataNotFoundError("missing")

    response = client.get("/api/v1/arks/ark:/12345/test001?info")

    assert response.status_code == 502
