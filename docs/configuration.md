# Resolver configuration

Settings are read from environment variables (`app/config.py`). A local `.env`
file is loaded when present; `.env.integration` takes precedence over it. In a
deployed stack the deployer generates the environment from the operator
inventory; do not edit generated files by hand.

| Variable | Default | Meaning |
|---|---|---|
| `RESOLVER_API_HOST` | `0.0.0.0` | Bind address for `run_server()` (the container command binds `0.0.0.0` itself) |
| `RESOLVER_API_PORT` | `8002` | Port for `run_server()`; the Dockerfile exposes `8002` |
| `RESOLVER_REDIRECT_STATUS` | `302` | HTTP status of the default redirect |
| `DARK_RPC_URL` | `http://localhost:8545` | Besu JSON-RPC endpoint |
| `DARK_CHAIN_ID` | `1337` | Expected chain ID (the platform default chain is `2025`; the inventory sets it) |
| `DARK_CONTRACT_ADDRESS` | *(empty, required)* | Address of the `dARK` contract; startup fails with `Missing required environment variable: DARK_CONTRACT_ADDRESS` if empty |
| `DARK_VALIDATE_CHAIN_ID` | `true` | Compare the RPC's chain ID with `DARK_CHAIN_ID` |
| `METADATA_STORAGE_TYPE` | `store_api` | `store_api` or `filesystem`; anything else fails at startup |
| `METADATA_STORAGE_PATH` | `./metadata_storage` | Directory for `filesystem` (opened read-only; must be the Minter's directory) |
| `METADATA_STORE_API_URL` | `http://localhost:8003` | Store API base URL for `store_api` (`http://store-api:8003` in the installed stack) |
| `METADATA_STORE_API_TIMEOUT_SECONDS` | `10.0` | HTTP timeout toward Store |

No signing key and no Authority contract address are needed: the client is
read-only.

## Ports and image

- Python 3.14 (`requires-python >=3.14,<3.15`), FastAPI and Uvicorn.
- The `Dockerfile` (`python:3.14-slim`, non-root `appuser`) copies
  `dark-core-resolver-api/` and `dark-core-lib/` from its build context and installs
  both, so it must be built from a context that contains the two directories side
  by side; the deployer assembles that context from its component checkouts.
- `CMD uvicorn app.main:app --host 0.0.0.0 --port 8002`; entry point script
  `dark-core-resolver-api` runs `app.main:run_server`.
