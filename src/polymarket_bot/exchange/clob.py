"""
CLOB API wrapper.

Wraps `py_clob_client` to expose a small, typed surface for the rest of the bot.
The strategy layer never imports `py_clob_client` directly — it only sees the
methods defined here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from polymarket_bot.config import PolymarketCredentials

log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class OrderBookSnapshot:
    """A point-in-time snapshot of one market's orderbook."""

    token_id: str
    best_bid: float
    best_ask: float
    bid_size: float
    ask_size: float
    timestamp_ms: int

    @property
    def midpoint(self) -> float:
        return (self.best_bid + self.best_ask) / 2

    @property
    def spread(self) -> float:
        return self.best_ask - self.best_bid


@dataclass(frozen=True)
class OrderResponse:
    order_id: str
    status: str
    filled_size: float = 0.0


class ClobExchange:
    """High-level wrapper around the Polymarket CLOB."""

    def __init__(self, creds: PolymarketCredentials, dry_run: bool = False) -> None:
        from py_clob_client.client import ClobClient

        self._dry_run = dry_run
        self._client = ClobClient(
            host=creds.clob_host,
            key=creds.private_key,
            chain_id=creds.chain_id,
            signature_type=creds.signature_type,
            funder=creds.funder_address,
        )
        if creds.api_key and creds.api_secret and creds.api_passphrase:
            from py_clob_client.clob_types import ApiCreds

            self._client.set_api_creds(
                ApiCreds(
                    api_key=creds.api_key,
                    api_secret=creds.api_secret,
                    api_passphrase=creds.api_passphrase,
                )
            )
        else:
            self._client.set_api_creds(self._client.create_or_derive_api_creds())
        log.info("clob.client_ready", host=creds.clob_host, dry_run=dry_run)

    # ---- Read --------------------------------------------------------------

    def get_orderbook(self, token_id: str) -> OrderBookSnapshot:
        book = self._client.get_order_book(token_id)
        # `book` shape: {bids: [{price, size}, ...], asks: [...]}
        bids = book.bids or []
        asks = book.asks or []
        if not bids or not asks:
            raise RuntimeError(f"empty orderbook for {token_id!r}")
        # Polymarket sorts bids descending and asks ascending
        return OrderBookSnapshot(
            token_id=token_id,
            best_bid=float(bids[0].price),
            best_ask=float(asks[0].price),
            bid_size=float(bids[0].size),
            ask_size=float(asks[0].size),
            timestamp_ms=int(book.timestamp or 0),
        )

    def get_midpoint(self, token_id: str) -> float:
        return float(self._client.get_midpoint(token_id).get("mid", 0))

    # ---- Write -------------------------------------------------------------

    def place_limit_order(
        self,
        token_id: str,
        side: str,
        price: float,
        size: float,
    ) -> OrderResponse:
        """Post a GTC limit order. Returns immediately with the order id."""
        if self._dry_run:
            log.info(
                "clob.dry_run_order",
                token_id=token_id,
                side=side,
                price=price,
                size=size,
            )
            return OrderResponse(order_id="DRY-RUN", status="dry_run")

        from py_clob_client.clob_types import OrderArgs, OrderType
        from py_clob_client.order_builder.constants import BUY, SELL

        args = OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side=BUY if side.upper() == "BUY" else SELL,
        )
        signed = self._client.create_order(args)
        resp = self._client.post_order(signed, OrderType.GTC)
        log.info("clob.order_posted", token_id=token_id, side=side, response=resp)
        return OrderResponse(
            order_id=str(resp.get("orderID", "")),
            status=str(resp.get("status", "unknown")),
        )

    def cancel_order(self, order_id: str) -> bool:
        if self._dry_run:
            log.info("clob.dry_run_cancel", order_id=order_id)
            return True
        resp = self._client.cancel(order_id)
        return bool(resp.get("success", False))

    def cancel_all(self) -> int:
        if self._dry_run:
            return 0
        resp = self._client.cancel_all()
        return len(resp.get("canceled", []))
