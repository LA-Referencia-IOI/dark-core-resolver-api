# Resolver operations

## Run locally

```bash
python3.14 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ../dark-core-lib          # SDK from the sibling checkout
export DARK_RPC_URL=http://localhost:8545
export DARK_CHAIN_ID=2025             # match your node; the application default is 1337
export DARK_CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS
export METADATA_STORE_API_URL=http://localhost:8003
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

The RPC/Store localhost URLs above require explicitly published services. For
the managed local inventory, follow the
[Docker-network development example](https://github.com/LA-Referencia-IOI/dark-deployer/blob/main/docs/developer-onboarding.md#6-iterate-without-rebuilding-an-image).
It also shows how to read the public contract address without exporting secrets.
Run this component in its own environment and from its own directory.

Then `curl -i http://localhost:8002/api/v1/arks/ark:NAAN/name` and add `?info` or
`?metadata` for the other views.

## Tests

```bash
pip install -e ../dark-core-lib
pytest                      # testpaths = tests
```

`tests/test_resolver.py` mocks the blockchain client and storage; no node is
needed. It covers redirect, `?info` without CIDs, raw `?metadata` (XML and JSON),
the `?info`+`?metadata` rejection, `404`, `502` on a missing Level 1, compact input
and rejection of repeated prefix slashes.

## In a deployment

- Declared in the inventory under `resolver.instances` (or created by the
  deployer's application model) with a Store reader and an RPC node; routed by an
  edge-proxy site.
- Probe with `GET /health/live` (process) and `GET /health` (chain + storage).
  Through the deployer: `./deploy.sh verify --deployment ID`.
- Logs: `./deploy.sh logs --deployment ID --service RESOLVER_SERVICE_ID`.

## Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Container exits at start with `Missing required environment variable: DARK_CONTRACT_ADDRESS` | Contract address not generated/set | Install completed contracts stage? Environment projection |
| `/health` is `degraded`, `blockchain_connected: false` | RPC unreachable or wrong `DARK_RPC_URL` / chain ID mismatch (`DARK_VALIDATE_CHAIN_ID=true`) | Besu RPC health; `DARK_CHAIN_ID` |
| `404` for a freshly minted ARK | Minter has not published yet (ARK still `R`/`D`) | Minter ARK status |
| `?info` is `502` `Published metadata not found in storage` | Level-1 CID not readable from this Store reader | Store `/v1/status/{cid}`, replication, reader binding |
| `?metadata` is `404` | Level-2 reference missing or content not found | Store and IPFS availability |
| Redirect works but `?info` fails | Storage outage; the redirect needs only the chain | Store API health |
| Filesystem backend finds nothing | Resolver not mounting the Minter's metadata directory read-only | `METADATA_STORAGE_PATH` |
