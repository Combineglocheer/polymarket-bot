"""
Risk manager — pre-trade checks that every Signal must pass before it becomes
an order. The Risk Manager is the last line of defense between a buggy
strategy and your wallet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import structlog

from polymarket_bot.config import RiskConfig
from polymarket_bot.strategies.base import Signal

log = structlog.get_logger(__name__)


@dataclass
class RiskState:
    """Mutable state tracked by the risk manager across the bot's lifetime."""

    realized_pnl_today: float = 0.0
    open_positions: int = 0
    last_pnl_date: date = field(default_factory=date.today)
    halted: bool = False
    halt_reason: str = ""


class RiskManager:
    def __init__(self, cfg: RiskConfig) -> None:
        self._cfg = cfg
        self._state = RiskState()

    @property
    def state(self) -> RiskState:
        return self._state

    def check(self, signal: Signal) -> tuple[bool, str]:
        """Return (allowed, reason)."""
        self._roll_pnl_if_new_day()

        if self._state.halted:
            return False, f"bot halted: {self._state.halt_reason}"

        notional = signal.price * signal.size
        if notional > self._cfg.max_position_size_usd:
            return False, (
                f"order notional ${notional:.2f} > cap "
                f"${self._cfg.max_position_size_usd:.2f}"
            )

        if (
            signal.side == "BUY"
            and self._state.open_positions >= self._cfg.max_open_positions
        ):
            return False, (
                f"already at max_open_positions={self._cfg.max_open_positions}"
            )

        if self._state.realized_pnl_today <= -self._cfg.daily_loss_limit_usd:
            self._halt("daily loss limit hit")
            return False, "daily loss limit hit"

        return True, "ok"

    def record_fill(self, side: str, pnl_delta: float) -> None:
        if side == "BUY":
            self._state.open_positions += 1
        elif side == "SELL":
            self._state.open_positions = max(0, self._state.open_positions - 1)
        self._state.realized_pnl_today += pnl_delta
        log.info(
            "risk.fill_recorded",
            open=self._state.open_positions,
            pnl_today=self._state.realized_pnl_today,
        )

    def _halt(self, reason: str) -> None:
        self._state.halted = True
        self._state.halt_reason = reason
        log.error("risk.halt", reason=reason)

    def _roll_pnl_if_new_day(self) -> None:
        today = date.today()
        if self._state.last_pnl_date != today:
            log.info(
                "risk.new_day",
                yesterday_pnl=self._state.realized_pnl_today,
            )
            self._state.realized_pnl_today = 0.0
            self._state.last_pnl_date = today
