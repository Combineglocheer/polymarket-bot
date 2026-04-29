"""Trading strategies. Subclass `BaseStrategy` to add your own."""

from polymarket_bot.strategies.base import BaseStrategy, Signal
from polymarket_bot.strategies.mean_reversion import MeanReversionStrategy
from polymarket_bot.strategies.market_making import MarketMakingStrategy

__all__ = [
    "BaseStrategy",
    "Signal",
    "MeanReversionStrategy",
    "MarketMakingStrategy",
]
