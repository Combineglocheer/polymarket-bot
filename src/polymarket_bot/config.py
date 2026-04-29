"""Configuration loaded from environment variables and YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PolymarketCredentials(BaseSettings):
    """Credentials loaded from .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POLYMARKET_",
        extra="ignore",
    )

    private_key: str = Field(..., description="Polygon wallet private key (0x...)")
    funder_address: str = Field(..., description="Address holding USDC on Polymarket")
    signature_type: int = Field(1, description="0=EOA, 1=Magic, 2=BrowserProxy")

    api_key: str | None = None
    api_secret: str | None = None
    api_passphrase: str | None = None

    clob_host: str = "https://clob.polymarket.com"
    gamma_host: str = "https://gamma-api.polymarket.com"
    data_host: str = "https://data-api.polymarket.com"
    chain_id: int = 137


class StrategyConfig(BaseModel):
    name: str
    params: dict[str, Any] = Field(default_factory=dict)


class RiskConfig(BaseModel):
    max_position_size_usd: float = 25.0
    max_open_positions: int = 5
    daily_loss_limit_usd: float = 100.0
    kill_switch_drawdown_pct: float = 20.0
    max_slippage_bps: int = 50  # 0.50%


class ExecutionConfig(BaseModel):
    scan_interval_seconds: int = 30
    order_type: str = "GTC"
    dry_run: bool = True


class BotConfig(BaseModel):
    """Top-level bot configuration loaded from `config.yaml`."""

    strategy: StrategyConfig
    risk: RiskConfig = Field(default_factory=RiskConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> BotConfig:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
