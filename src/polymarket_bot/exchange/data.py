"""
Data API wrapper — positions, trade history, account balances.

The Data API is read-only and tracks every user's portfolio. The bot uses it
to know what we already own (so we don't double up) and to compute realized P&L.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class Position:
    asset: str  # token_id
    market: str  # condition_id
    size: float
    avg_price: float
    realized_pnl: float
    cur_price: float


class DataClient:
    """Read-only Polymarket Data API."""

    def __init__(self, host: str = "https://data-api.polymarket.com") -> None:
        self._client = httpx.Client(base_url=host, timeout=10.0)

    def get_positions(self, user_address: str) -> list[Position]:
        resp = self._client.get(
            "/positions",
            params={"user": user_address, "sizeThreshold": 1.0},
        )
        resp.raise_for_status()
        return [
            Position(
                asset=str(p.get("asset", "")),
                market=str(p.get("conditionId", "")),
                size=float(p.get("size", 0)),
                avg_price=float(p.get("avgPrice", 0)),
                realized_pnl=float(p.get("realizedPnl", 0)),
                cur_price=float(p.get("curPrice", 0)),
            )
            for p in resp.json()
        ]

    def get_value(self, user_address: str) -> float:
        """Total portfolio value in USDC."""
        resp = self._client.get("/value", params={"user": user_address})
        resp.raise_for_status()
        return float(resp.json().get("value", 0))
