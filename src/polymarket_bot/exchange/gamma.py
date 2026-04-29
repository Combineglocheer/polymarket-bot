"""
Gamma API wrapper — market discovery and metadata.

The Gamma API is a read-only HTTP service that exposes Polymarket's market
catalog, event structure, and metadata. Use it to find markets to trade;
do NOT use it for live prices (use the CLOB API for that).
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import structlog

log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class Market:
    """Lightweight view of a Polymarket market."""

    condition_id: str
    question: str
    yes_token_id: str
    no_token_id: str
    volume_24h_usd: float
    liquidity_usd: float
    end_date_iso: str
    category: str
    active: bool
    closed: bool


class GammaClient:
    """Read-only client for the Polymarket Gamma API."""

    def __init__(self, host: str = "https://gamma-api.polymarket.com") -> None:
        self._client = httpx.Client(base_url=host, timeout=10.0)

    def list_markets(
        self,
        *,
        active: bool = True,
        closed: bool = False,
        limit: int = 100,
        order: str = "volume",
    ) -> list[Market]:
        """List markets sorted by `order` (volume, liquidity, endDate)."""
        params = {
            "active": str(active).lower(),
            "closed": str(closed).lower(),
            "limit": limit,
            "order": order,
            "ascending": "false",
        }
        resp = self._client.get("/markets", params=params)
        resp.raise_for_status()
        return [self._parse_market(m) for m in resp.json() if self._has_tokens(m)]

    def get_market(self, condition_id: str) -> Market:
        resp = self._client.get(f"/markets/{condition_id}")
        resp.raise_for_status()
        return self._parse_market(resp.json())

    @staticmethod
    def _has_tokens(raw: dict) -> bool:
        # Some markets in the Gamma response don't expose token IDs (e.g., draft).
        toks = raw.get("clobTokenIds")
        return bool(toks) and len(toks) >= 2

    @staticmethod
    def _parse_market(raw: dict) -> Market:
        import json as _json

        tokens = raw.get("clobTokenIds")
        if isinstance(tokens, str):
            tokens = _json.loads(tokens)
        return Market(
            condition_id=str(raw.get("conditionId", "")),
            question=str(raw.get("question", "")),
            yes_token_id=str(tokens[0]) if tokens else "",
            no_token_id=str(tokens[1]) if tokens and len(tokens) > 1 else "",
            volume_24h_usd=float(raw.get("volume24hr", 0) or 0),
            liquidity_usd=float(raw.get("liquidity", 0) or 0),
            end_date_iso=str(raw.get("endDate", "")),
            category=str(raw.get("category", "")),
            active=bool(raw.get("active", False)),
            closed=bool(raw.get("closed", False)),
        )
