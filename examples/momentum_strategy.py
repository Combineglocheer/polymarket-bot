"""
Example: a 30-line custom strategy.

Run with:
    polymarket-bot run --strategy momentum --config examples/momentum_config.yaml

(Drop a copy of this file in `src/polymarket_bot/strategies/` to enable it.)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from polymarket_bot.strategies.base import BaseStrategy, Signal


@dataclass
class MomentumStrategy(BaseStrategy):
    name: str = "momentum"

    window: int = 20
    z_threshold: float = 2.0
    order_size_usd: float = 5.0
    _history: dict[str, deque[float]] = field(default_factory=dict)

    def evaluate(self, market, orderbook, position):  # type: ignore[override]
        hist = self._history.setdefault(orderbook.token_id, deque(maxlen=self.window))
        hist.append(orderbook.midpoint)
        if len(hist) < self.window:
            return None

        mean = sum(hist) / len(hist)
        var = sum((x - mean) ** 2 for x in hist) / len(hist)
        std = var**0.5
        if std == 0:
            return None
        z = (orderbook.midpoint - mean) / std

        # Strong upward momentum -> buy YES
        if z >= self.z_threshold and position is None:
            size = round(self.order_size_usd / orderbook.best_ask, 2)
            return Signal.buy(
                token_id=orderbook.token_id,
                price=orderbook.best_ask,
                size=size,
                reason=f"momentum z={z:.2f}",
            )
        return None
