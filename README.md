# dark-core-resolver-api

Read-only ARK resolution service backed by blockchain and shared metadata storage.

## Overview

`dark-core-resolver-api` is the public read-only side of the dARK stack. Blockchain is the source of truth for ARK existence and target URLs. Metadata is completed from the same storage backend used by the minter, through the shared abstractions in `dark-core-lib`.

The service does not keep:

- local lifecycle database
- worker process
- write endpoints

## Behavior

- `GET /api/v1/arks/{ark}` redirects to the on-chain target.
- `GET /api/v1/arks/{ark}?info` returns a public Level-1 projection.
- `GET /api/v1/arks/{ark}?metadata` returns Level-2 raw metadata in its original media type.

Public responses intentionally hide internal CIDs. They are used only inside the resolution pipeline.

## Resolution Model

```text
blockchain cid -> load L1 from shared storage -> optionally load L2 from L1.original_metadata.cid
```

- default resolution uses only the on-chain target
- `?info` uses blockchain + L1
- `?metadata` uses blockchain + L1 + L2

## Shared Dependencies

This service relies on `dark-core-lib` for:

- `DARKCoreClient` in `read_only=True`
- `parse_ark_id(...)`
- `dark_core_lib.metadata.MetadataService`
- `dark_core_lib.metadata.get_metadata_storage(...)`

That keeps the minter and resolver aligned on:

- the Level-1 schema
- the Level-2 reference shape
- storage backends and content-type handling

## Operational Notes

- with `METADATA_STORAGE_TYPE=filesystem`, the resolver must mount the same metadata directory as the minter in read-only mode
- with `METADATA_STORAGE_TYPE=store_api`, the resolver must point to the same remote store backend
- if storage is unavailable, default redirect can still work as long as blockchain resolution is healthy
