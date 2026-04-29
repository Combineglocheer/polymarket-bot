"""
Main bot orchestrator.

PolymarketBot wires together:
    * GammaClient (market discovery)
    * ClobExchange (orderbook + execution)
    * DataClient (positions + P&L)
    * BaseStrategy (decision logic)
    * RiskManager (pre-trade checks)

The main loop is intentionally simple — read state, evaluate, act.
"""

from __future__ import annotations

import time
from pathlib import Path

import structlog

from polymarket_bot.config import BotConfig, PolymarketCredentials
from polymarket_bot.exchange import ClobExchange, DataClient, GammaClient
from polymarket_bot.risk import RiskManager
from polymarket_bot.strategies.base import BaseStrategy
from polymarket_bot.strategies.market_making import MarketMakingStrategy
from polymarket_bot.strategies.mean_reversion import MeanReversionStrategy

log = structlog.get_logger(__name__)


_BUILTIN_STRATEGIES: dict[str, type[BaseStrategy]] = {
    "mean_reversion": MeanReversionStrategy,
    "market_making": MarketMakingStrategy,
}


class PolymarketBot:
    """Top-level bot orchestrator."""

    def __init__(
        self,
        creds: PolymarketCredentials,
        config: BotConfig,
        strategy: BaseStrategy,
    ) -> None:
        self._creds = creds
        self._config = config
        self._strategy = strategy
        self._clob = ClobExchange(creds, dry_run=config.execution.dry_run)
        self._gamma = GammaClient(creds.gamma_host)
        self._data = DataClient(creds.data_host)
        self._risk = RiskManager(config.risk)

    # ---- Construction shortcuts -------------------------------------------

    @classmethod
    def from_env(
        cls,
        config_path: str | Path = "config.yaml",
        strategy: BaseStrategy | None = None,
    ) -> PolymarketBot:
        creds = PolymarketCredentials()  # type: ignore[call-arg]
        config = BotConfig.from_yaml(config_path)
        if strategy is None:
            strategy = build_strategy(config)
        return cls(creds=creds, config=config, strategy=strategy)

    # ---- Main loop --------------------------------------------------------

    def run(self) -> None:
        log.info(
            "bot.starting",
            strategy=self._strategy.name,
            dry_run=self._config.execution.dry_run,
        )
        try:
            while True:
                self._tick()
                time.sleep(self._config.execution.scan_interval_seconds)
        except KeyboardInterrupt:
            log.info("bot.stopped_by_user")
            self._clob.cancel_all()

    def _tick(self) -> None:
        markets = self._gamma.list_markets(active=True, closed=False, limit=100)
        log.info("bot.markets_fetched", n=len(markets))
        positions = self._data.get_positions(self._creds.funder_address)
        pos_by_token = {p.asset: p for p in positions}

        for market in markets:
            for token_id in (market.yes_token_id, market.no_token_id):
                if not token_id:
                    continue
                try:
                    book = self._clob.get_orderbook(token_id)
                except Exception as exc:  # noqa: BLE001
                    log.debug("bot.skip_no_book", token_id=token_id, err=str(exc))
                    continue
                signal = self._strategy.evaluate(
                    market=market,
                    orderbook=book,
                    position=pos_by_token.get(token_id),
                )
                if signal is None:
                    continue
                allowed, reason = self._risk.check(signal)
                if not allowed:
                    log.info("bot.signal_rejected", reason=reason)
                    continue
                self._clob.place_limit_order(
                    token_id=signal.token_id,
                    side=signal.side,
                    price=signal.price,
                    size=signal.size,
                )
                self._risk.record_fill(signal.side, pnl_delta=0.0)


def build_strategy(config: BotConfig) -> BaseStrategy:
    """Instantiate a built-in strategy from config."""
    name = config.strategy.name
    cls = _BUILTIN_STRATEGIES.get(name)
    if cls is None:
        raise ValueError(
            f"unknown strategy {name!r}. "
            f"Built-ins: {sorted(_BUILTIN_STRATEGIES)}. "
            f"Drop a custom one in `strategies/` and import it."
        )
    return cls(**config.strategy.params)
