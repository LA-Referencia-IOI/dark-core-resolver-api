# dark-core-resolver-api

Read-only ARK resolution service backed by blockchain and shared metadata storage.

## Overview

`dark-core-resolver-api` is the public read-only side of the dARK stack.

- blockchain is the source of truth for ARK existence and target URLs
- L1 is always stored as JSON
- L2 is stored as raw bytes
- `dark-store-api` is raw storage only; the resolver reconstructs L2 semantics from `L1.original_metadata`

The service does not keep:

- local lifecycle database
- worker process
- write endpoints

## Behavior

- `GET /api/v1/arks/{ark}` redirects to the on-chain target
- `GET /api/v1/arks/{ark}?info` returns a public Level-1 projection
- `GET /api/v1/arks/{ark}?metadata` returns Level-2 raw metadata with the media type declared in `L1.original_metadata.media_type`

Public responses intentionally hide internal CIDs. They are used only inside the resolution pipeline.

## Resolution Model

```text
blockchain cid -> load raw L1 JSON from shared storage -> load raw L2 bytes from shared storage
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
- the Level-2 reference shape: `schema`, `media_type`, `cid`
- content-type reconstruction for `?metadata`

## Operational Notes

- default runtime is `METADATA_STORAGE_TYPE=store_api`
- default public port is `8002`
- default local store URL is `http://localhost:8003`
- inside the installed Docker stack, the resolver points to `http://store-api:8003`
- with `METADATA_STORAGE_TYPE=filesystem`, the resolver must mount the same metadata directory as the minter in read-only mode
- if storage is unavailable, default redirect can still work as long as blockchain resolution is healthy
