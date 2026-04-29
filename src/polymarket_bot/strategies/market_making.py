"""
Simple symmetric market-making strategy.

Posts a bid and an ask `spread/2` away from the midpoint. Polymarket pays
0% maker fees, so a passive market maker collects the bid-ask spread when
both sides get hit.

Real production market makers add:
    * inventory skew (lean prices when long/short)
    * volatility-aware spread
    * cancel-on-fill / requote logic
    * cross-market hedging
"""

from __future__ import annotations

from dataclasses import dataclass

from polymarket_bot.strategies.base import BaseStrategy, Signal


@dataclass
class MarketMakingStrategy(BaseStrategy):
    name: str = "market_making"

    half_spread: float = 0.02
    order_size_usd: float = 5.0
    min_volume_usd: float = 100_000.0
    min_midpoint: float = 0.10
    max_midpoint: float = 0.90  # avoid pinned markets

    def evaluate(self, market, orderbook, position):  # type: ignore[override]
        if market.volume_24h_usd < self.min_volume_usd:
            return None

        mid = orderbook.midpoint
        if not (self.min_midpoint <= mid <= self.max_midpoint):
            return None

        # If we already hold inventory, fade it: only post the opposite side.
        if position is not None and position.size > 0:
            sell_price = round(min(0.99, mid + self.half_spread), 2)
            return Signal.sell(
                token_id=orderbook.token_id,
                price=sell_price,
                size=position.size,
                reason=f"MM exit at {sell_price:.2f}",
            )

        bid_price = round(max(0.01, mid - self.half_spread), 2)
        size = round(self.order_size_usd / bid_price, 2)
        return Signal.buy(
            token_id=orderbook.token_id,
            price=bid_price,
            size=size,
            reason=f"MM bid at {bid_price:.2f} (mid={mid:.2f})",
        )
