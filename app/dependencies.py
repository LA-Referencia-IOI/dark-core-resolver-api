"""Dependency injection for the resolver service."""

import logging
from typing import Optional

from dark_core_lib import CoreConfig, DARKCoreClient, get_metadata_storage as build_metadata_storage
from dark_core_lib.metadata import MetadataStorage

from app.config import get_settings


logger = logging.getLogger(__name__)

_corelib_client: Optional[DARKCoreClient] = None
_metadata_storage: Optional[MetadataStorage] = None


def get_corelib_client() -> DARKCoreClient:
    """Return the shared read-only DARKCoreClient instance."""
    global _corelib_client
    if _corelib_client is None:
        raise RuntimeError("dark-core-lib client not initialized")
    return _corelib_client


def init_corelib_client() -> DARKCoreClient:
    """Initialize the read-only blockchain client."""
    global _corelib_client
    settings = get_settings()
    settings.validate_blockchain_config()

    config = CoreConfig(
        rpc_url=settings.dark_rpc_url,
        chain_id=settings.dark_chain_id,
        dark_contract_address=settings.dark_contract_address,
        read_only=True,
        validate_chain_id=settings.dark_validate_chain_id,
    )

    _corelib_client = DARKCoreClient(config)
    logger.info("Initialized read-only DARKCoreClient")
    return _corelib_client


def shutdown_corelib_client() -> None:
    """Release the shared blockchain client."""
    global _corelib_client
    _corelib_client = None


def get_metadata_storage() -> MetadataStorage:
    """Return the configured metadata storage backend."""
    global _metadata_storage
    if _metadata_storage is None:
        raise RuntimeError("metadata storage not initialized")
    return _metadata_storage


def init_metadata_storage() -> MetadataStorage:
    """Initialize the configured metadata storage backend."""
    global _metadata_storage
    settings = get_settings()
    storage_type = settings.metadata_storage_type.lower()

    if storage_type == "filesystem":
        _metadata_storage = build_metadata_storage(
            storage_type="filesystem",
            storage_path=settings.metadata_storage_path,
            read_only=True,
        )
    elif storage_type == "store_api":
        _metadata_storage = build_metadata_storage(
            storage_type="store_api",
            store_api_url=settings.metadata_store_api_url,
            timeout_seconds=settings.metadata_store_api_timeout_seconds,
        )
    else:
        raise ValueError(f"Unsupported metadata storage type: {settings.metadata_storage_type}")

    logger.info("Initialized metadata storage backend: %s", storage_type)
    return _metadata_storage


def shutdown_metadata_storage() -> None:
    """Release the shared metadata storage backend."""
    global _metadata_storage
    _metadata_storage = None
