"""
Polymarket Bot — Automated trading bot for Polymarket prediction markets.

Public API:
    PolymarketBot     — main orchestrator
    BaseStrategy      — subclass to write your own strategy
    Signal            — value returned by a strategy

Quick start:
    >>> from polymarket_bot import PolymarketBot
    >>> bot = PolymarketBot.from_env()
    >>> bot.run()
"""

from polymarket_bot.bot import PolymarketBot
from polymarket_bot.strategies.base import BaseStrategy, Signal

__version__ = "0.1.0"
__all__ = ["PolymarketBot", "BaseStrategy", "Signal", "__version__"]
