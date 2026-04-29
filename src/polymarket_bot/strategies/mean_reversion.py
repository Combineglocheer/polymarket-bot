"""
Mean-reversion strategy.

Buys YES shares trading below `lower_bound` (oversold) on the assumption
that the market is mispricing a low-probability outcome. Closes when price
reverts toward the midpoint or hits `upper_bound`.

This is a REFERENCE implementation. It is not alpha. You'll want to add:
    * volatility filter
    * news/event filter
    * dynamic sizing
"""

from __future__ import annotations

from dataclasses import dataclass

from polymarket_bot.strategies.base import BaseStrategy, Signal


@dataclass
class MeanReversionStrategy(BaseStrategy):
    name: str = "mean_reversion"

    lower_bound: float = 0.05
    upper_bound: float = 0.30
    min_volume_usd: float = 50_000.0
    max_spread: float = 0.03
    order_size_usd: float = 10.0

    def evaluate(self, market, orderbook, position):  # type: ignore[override]
        # Liquidity & spread filters
        if market.volume_24h_usd < self.min_volume_usd:
            return None
        if orderbook.spread > self.max_spread:
            return None

        # Already in this market? Look for an exit.
        if position is not None and position.size > 0:
            if orderbook.best_bid >= self.upper_bound:
                return Signal.sell(
                    token_id=orderbook.token_id,
                    price=orderbook.best_bid,
                    size=position.size,
                    reason=f"exit at {orderbook.best_bid:.3f}",
                )
            return None

        # Look for an entry on the YES side.
        if (
            orderbook.token_id == market.yes_token_id
            and self.lower_bound <= orderbook.best_ask <= self.upper_bound
        ):
            size = round(self.order_size_usd / orderbook.best_ask, 2)
            return Signal.buy(
                token_id=orderbook.token_id,
                price=orderbook.best_ask,
                size=size,
                reason=f"oversold YES at {orderbook.best_ask:.3f}",
            )
        return None
