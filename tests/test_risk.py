"""Unit tests for the risk manager."""

from __future__ import annotations

from polymarket_bot.config import RiskConfig
from polymarket_bot.risk import RiskManager
from polymarket_bot.strategies.base import Signal


def _signal(price: float = 0.50, size: float = 10.0) -> Signal:
    return Signal.buy(token_id="t", price=price, size=size)


def test_allows_normal_order():
    rm = RiskManager(RiskConfig(max_position_size_usd=100))
    ok, _ = rm.check(_signal(price=0.50, size=10.0))
    assert ok


def test_rejects_oversized_order():
    rm = RiskManager(RiskConfig(max_position_size_usd=5))
    ok, reason = rm.check(_signal(price=0.50, size=100.0))
    assert not ok
    assert "cap" in reason


def test_rejects_when_over_max_open_positions():
    rm = RiskManager(RiskConfig(max_open_positions=1))
    rm.record_fill("BUY", pnl_delta=0.0)
    ok, reason = rm.check(_signal())
    assert not ok
    assert "max_open_positions" in reason


def test_halts_after_daily_loss():
    rm = RiskManager(RiskConfig(daily_loss_limit_usd=10))
    rm.record_fill("BUY", pnl_delta=-15)  # blew the limit
    ok, _ = rm.check(_signal())
    assert not ok
    assert rm.state.halted
