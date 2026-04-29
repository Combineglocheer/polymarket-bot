"""Base classes for strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from polymarket_bot.exchange.clob import OrderBookSnapshot
    from polymarket_bot.exchange.data import Position
    from polymarket_bot.exchange.gamma import Market


@dataclass(frozen=True)
class Signal:
    """A trade signal emitted by a strategy."""

    token_id: str
    side: Literal["BUY", "SELL"]
    price: float
    size: float
    reason: str = ""

    @classmethod
    def buy(cls, token_id: str, price: float, size: float, reason: str = "") -> Signal:
        return cls(token_id=token_id, side="BUY", price=price, size=size, reason=reason)

    @classmethod
    def sell(cls, token_id: str, price: float, size: float, reason: str = "") -> Signal:
        return cls(token_id=token_id, side="SELL", price=price, size=size, reason=reason)


class BaseStrategy(ABC):
    """Subclass and override `evaluate` to define a new strategy."""

    name: str = "base"

    @abstractmethod
    def evaluate(
        self,
        market: Market,
        orderbook: OrderBookSnapshot,
        position: Position | None,
    ) -> Signal | None:
        """
        Decide whether to trade this market.

        Return:
            * a `Signal` to place an order
            * `None` to skip
        """
        ...
