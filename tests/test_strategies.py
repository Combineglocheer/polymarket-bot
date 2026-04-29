"""Unit tests for the built-in strategies."""

from __future__ import annotations

from dataclasses import dataclass

from polymarket_bot.strategies.mean_reversion import MeanReversionStrategy
from polymarket_bot.strategies.market_making import MarketMakingStrategy


@dataclass
class _FakeMarket:
    yes_token_id: str = "YES"
    no_token_id: str = "NO"
    volume_24h_usd: float = 100_000.0
    condition_id: str = "0xabc"
    question: str = "Will X happen?"
    liquidity_usd: float = 50_000.0
    end_date_iso: str = "2026-12-31"
    category: str = "Politics"
    active: bool = True
    closed: bool = False


@dataclass
class _FakeBook:
    token_id: str
    best_bid: float
    best_ask: float
    bid_size: float = 1000.0
    ask_size: float = 1000.0
    timestamp_ms: int = 0

    @property
    def midpoint(self) -> float:
        return (self.best_bid + self.best_ask) / 2

    @property
    def spread(self) -> float:
        return self.best_ask - self.best_bid


# ---- Mean reversion --------------------------------------------------------


def test_mean_reversion_buys_oversold_yes():
    strat = MeanReversionStrategy(lower_bound=0.05, upper_bound=0.30)
    book = _FakeBook(token_id="YES", best_bid=0.07, best_ask=0.08)
    sig = strat.evaluate(_FakeMarket(), book, position=None)
    assert sig is not None
    assert sig.side == "BUY"
    assert sig.token_id == "YES"


def test_mean_reversion_skips_when_outside_band():
    strat = MeanReversionStrategy(lower_bound=0.05, upper_bound=0.30)
    book = _FakeBook(token_id="YES", best_bid=0.45, best_ask=0.46)
    assert strat.evaluate(_FakeMarket(), book, position=None) is None


def test_mean_reversion_skips_when_volume_too_low():
    strat = MeanReversionStrategy(min_volume_usd=200_000)
    book = _FakeBook(token_id="YES", best_bid=0.07, best_ask=0.08)
    assert strat.evaluate(_FakeMarket(volume_24h_usd=1000), book, None) is None


def test_mean_reversion_skips_when_spread_too_wide():
    strat = MeanReversionStrategy(max_spread=0.01)
    book = _FakeBook(token_id="YES", best_bid=0.05, best_ask=0.10)
    assert strat.evaluate(_FakeMarket(), book, None) is None


# ---- Market making ---------------------------------------------------------


def test_market_making_posts_bid_when_flat():
    strat = MarketMakingStrategy(half_spread=0.02, min_volume_usd=10_000)
    book = _FakeBook(token_id="YES", best_bid=0.49, best_ask=0.51)
    sig = strat.evaluate(_FakeMarket(), book, position=None)
    assert sig is not None
    assert sig.side == "BUY"
    assert sig.price < book.midpoint


def test_market_making_skips_pinned_markets():
    strat = MarketMakingStrategy(min_midpoint=0.10, max_midpoint=0.90)
    book = _FakeBook(token_id="YES", best_bid=0.97, best_ask=0.98)
    assert strat.evaluate(_FakeMarket(), book, None) is None
