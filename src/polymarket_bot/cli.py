"""
Polymarket Bot — Command Line Interface.

Run `polymarket-bot --help` for the full command list.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from polymarket_bot.bot import PolymarketBot
from polymarket_bot.config import BotConfig, PolymarketCredentials
from polymarket_bot.exchange import DataClient, GammaClient
from polymarket_bot.utils.logging import setup_logging

app = typer.Typer(
    name="polymarket-bot",
    help="Automated trading bot for Polymarket prediction markets.",
    no_args_is_help=True,
)
markets_app = typer.Typer(help="Inspect Polymarket markets.")
order_app = typer.Typer(help="Place and cancel orders.")
app.add_typer(markets_app, name="markets")
app.add_typer(order_app, name="order")

console = Console()


@app.command()
def run(
    config: Path = typer.Option("config.yaml", help="Path to config.yaml"),
    strategy: str | None = typer.Option(None, help="Override strategy name"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't place real orders"),
    log_level: str = typer.Option("INFO", help="DEBUG / INFO / WARNING / ERROR"),
) -> None:
    """Start the bot's main trading loop."""
    setup_logging(log_level)
    cfg = BotConfig.from_yaml(config)
    if strategy:
        cfg.strategy.name = strategy
    if dry_run:
        cfg.execution.dry_run = True
    bot = PolymarketBot.from_env(config_path=config)
    bot._config = cfg  # honor CLI overrides
    bot.run()


@markets_app.command("list")
def markets_list(
    sort_by: str = typer.Option("volume", help="volume | liquidity | endDate"),
    limit: int = typer.Option(10, help="How many to show"),
) -> None:
    """List active Polymarket markets, sorted."""
    setup_logging("WARNING")
    gamma = GammaClient()
    markets = gamma.list_markets(order=sort_by, limit=limit)

    table = Table(title=f"Top {len(markets)} active Polymarket markets by {sort_by}")
    table.add_column("Question", overflow="fold", max_width=50)
    table.add_column("24h Vol", justify="right")
    table.add_column("Liquidity", justify="right")
    table.add_column("Category")

    for m in markets:
        table.add_row(
            m.question,
            f"${m.volume_24h_usd:,.0f}",
            f"${m.liquidity_usd:,.0f}",
            m.category or "-",
        )
    console.print(table)


@app.command()
def portfolio() -> None:
    """Show open positions and P&L."""
    setup_logging("WARNING")
    creds = PolymarketCredentials()  # type: ignore[call-arg]
    data = DataClient(creds.data_host)
    positions = data.get_positions(creds.funder_address)
    value = data.get_value(creds.funder_address)

    table = Table(title=f"Portfolio — total value ${value:,.2f}")
    table.add_column("Market", overflow="fold", max_width=50)
    table.add_column("Size", justify="right")
    table.add_column("Avg", justify="right")
    table.add_column("Cur", justify="right")
    table.add_column("Realized PnL", justify="right")

    for p in positions:
        table.add_row(
            p.market[:10] + "…",
            f"{p.size:.2f}",
            f"{p.avg_price:.3f}",
            f"{p.cur_price:.3f}",
            f"${p.realized_pnl:.2f}",
        )
    console.print(table)


@order_app.command("place")
def order_place(
    token_id: str = typer.Option(..., help="Polymarket CLOB token ID"),
    side: str = typer.Option(..., help="BUY or SELL"),
    price: float = typer.Option(..., help="Limit price (0.01 - 0.99)"),
    size: float = typer.Option(..., help="Number of shares"),
) -> None:
    """Place a single GTC limit order."""
    setup_logging("INFO")
    creds = PolymarketCredentials()  # type: ignore[call-arg]
    from polymarket_bot.exchange.clob import ClobExchange

    clob = ClobExchange(creds)
    resp = clob.place_limit_order(
        token_id=token_id, side=side.upper(), price=price, size=size
    )
    console.print(f"[green]Posted:[/green] {resp}")


@app.command()
def version() -> None:
    """Print the installed version."""
    from polymarket_bot import __version__

    console.print(f"polymarket-bot {__version__}")


if __name__ == "__main__":
    app()
