"""Configuration settings for dARK Core Resolver API."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> str:
    """Prefer local integration settings when present."""
    project_root = Path(__file__).resolve().parents[1]
    integration_env = project_root / ".env.integration"
    default_env = project_root / ".env"
    if integration_env.exists():
        return str(integration_env)
    return str(default_env)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )

    resolver_api_host: str = Field(default="0.0.0.0", alias="RESOLVER_API_HOST")
    resolver_api_port: int = Field(default=8002, alias="RESOLVER_API_PORT")
    resolver_redirect_status: int = Field(default=302, alias="RESOLVER_REDIRECT_STATUS")

    metadata_storage_type: str = Field(default="store_api", alias="METADATA_STORAGE_TYPE")
    metadata_storage_path: str = Field(default="./metadata_storage", alias="METADATA_STORAGE_PATH")
    metadata_store_api_url: str = Field(default="http://localhost:8003", alias="METADATA_STORE_API_URL")
    metadata_store_api_timeout_seconds: float = Field(
        default=10.0,
        alias="METADATA_STORE_API_TIMEOUT_SECONDS",
    )

    dark_rpc_url: str = Field(default="http://localhost:8545", alias="DARK_RPC_URL")
    dark_chain_id: int = Field(default=1337, alias="DARK_CHAIN_ID")
    dark_contract_address: str = Field(default="", alias="DARK_CONTRACT_ADDRESS")
    dark_validate_chain_id: bool = Field(default=True, alias="DARK_VALIDATE_CHAIN_ID")

    def validate_blockchain_config(self) -> None:
        """Validate minimal blockchain configuration required for read-only mode."""
        if not self.dark_contract_address:
            raise ValueError("Missing required environment variable: DARK_CONTRACT_ADDRESS")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings(_env_file=_resolve_env_file())
