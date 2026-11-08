# Resolver API reference

Base URL: the service root. Interactive documentation: `/docs` (Swagger UI) and
`/redoc`. Authentication: none; the service is public and read-only. CORS allows
all origins.

## Resolution

`GET` or `HEAD /api/v1/arks/{ark}`

`{ark}` is a path, so slashes are allowed: `ark:NAAN/name` (compact) or
`ark:/NAAN/name` (classic). Behind the deployer's edge proxy the public route
usually maps `/` to this path, so users see `https://host/ark:NAAN/name`.

| Query | Response | Reads |
|---|---|---|
| *(none)* | Redirect to the on-chain `url` with `RESOLVER_REDIRECT_STATUS` (default `302`) | Chain |
| `?info` | `200` JSON `ArkInfoResponse` | Chain + Level 1 |
| `?metadata` | `200` raw Level-2 document with its original `Content-Type` | Chain + Level 1 + Level 2 |
| `?info&metadata` | `400` `Use either ?info or ?metadata, not both` | none |

### `ArkInfoResponse`

| Field | Source |
|---|---|
| `ark` | Canonical ARK from the chain |
| `target` | On-chain `url` |
| `created_at`, `updated_at` | On-chain timestamps |
| `metadata_schema` | `original_metadata.schema` of Level 1 |
| `title`, `authors`, `year`, `publisher`, `resource_type`, `language`, `abstract`, `subjects`, `rights`, `alternate_urls` | Level 1 |
| `alternate_identifiers` | List of `{schema, value}` or `null` when absent |

The `?info` projection does not include the internal metadata CIDs. The raw
`?metadata` document is returned unchanged and may itself contain identifiers.

### Errors

Error bodies are `{"detail": "..."}`.

| Status | Cause |
|---|---|
| `400` | Malformed ARK, `?info` with `?metadata`, any uncaught `ValueError` |
| `404` | ARK not found on chain; Level-2 missing or not found (`?metadata`) |
| `502` | Blockchain error; Level-1 missing/not found/invalid; storage backend unavailable |

## Health

| Path | Behavior |
|---|---|
| `GET /health/live` | `{"status": "alive"}`; no RPC or storage call |
| `GET /health` | Calls the chain (`blockchain_connected`, `current_block`) and storage (`metadata_storage`: `healthy` / `unhealthy`). Always `200`; `status` is `healthy` or `degraded` with an error field |

There are no `/health/read` or `/health/write` endpoints in this service (those
belong to the Store API).
