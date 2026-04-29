# Polymarket Bot — Automated Trading Bot for Polymarket Prediction Markets

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen.svg)](#)
[![Polymarket CLOB](https://img.shields.io/badge/Polymarket-CLOB%20API-7c3aed.svg)](https://docs.polymarket.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

> **Polymarket Bot** is an open-source, production-ready **automated trading bot for Polymarket** — the world's largest prediction market. Built in Python on top of the official `py-clob-client`, it scans markets, evaluates configurable strategies, and places orders on the Polymarket CLOB API automatically, 24/7.

If you searched for **"polymarket bot"**, **"polymarket trading bot"**, **"polymarket python bot"**, **"polymarket api bot"**, or **"prediction market bot"** — you're in the right place.

---

## 📖 Table of Contents

- [What is Polymarket Bot?](#what-is-polymarket-bot)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Trading Strategies](#-trading-strategies)
- [Usage Examples](#-usage-examples)
- [Architecture](#-architecture)
- [Risk Management](#-risk-management)
- [Deployment (VPS / Docker)](#-deployment)
- [FAQ](#-faq)
- [Disclaimer](#-disclaimer)
- [Contributing](#-contributing)
- [License](#-license)

---

## What is Polymarket Bot?

**Polymarket** is a decentralized prediction market built on Polygon where users trade YES/NO shares on real-world events — elections, crypto prices, sports, geopolitics. Each share resolves to either $1.00 (correct) or $0.00 (wrong), so the live price effectively reflects the market-implied probability.

**Polymarket Bot** is a Python toolkit that automates trading on Polymarket. Instead of manually clicking through markets, the bot:

1. Connects to the **Polymarket CLOB API** and **Gamma API**
2. Discovers active markets matching your filters (volume, category, spread)
3. Evaluates each market against pluggable strategies (mean-reversion, market-making, arbitrage, ML signals)
4. Places, monitors, and cancels orders programmatically with full position and risk management
5. Logs every action and exposes Prometheus-style metrics

This is **not** a simulator and **not** a backtesting-only tool — it places real orders on the production Polymarket CLOB. Polymarket has **no testnet**, so always start with small position sizes.

## ✨ Features

- 🚀 **Official SDK integration** — uses `py-clob-client` v2 with EIP-712 signing
- 📊 **Multi-strategy engine** — mean-reversion, market-making, arbitrage, custom user strategies
- 🔌 **Three Polymarket APIs covered** — CLOB (trading), Gamma (markets), Data (positions)
- 🌐 **WebSocket streaming** — real-time order book updates instead of polling
- 🛡️ **Risk management** — position limits, max drawdown, kill-switch, daily loss caps
- 📈 **Backtester** — replay historical orderbook data before going live
- 🧪 **Dry-run mode** — simulate trades without placing real orders
- 🐳 **Docker-ready** — one-command deployment to any VPS
- 📝 **Structured logging** — JSON logs, Prometheus metrics, Grafana dashboard included
- ⚙️ **Fully configurable** — YAML config, no code changes needed for new strategies
- 🔐 **Secure secrets** — `.env` based, supports HashiCorp Vault and AWS Secrets Manager
- 🧩 **Pluggable** — write a 30-line strategy class and the bot picks it up

## 🧠 How It Works

```
        ┌──────────────────────────────────────────────────┐
        │              Polymarket Bot Engine               │
        │                                                  │
        │   ┌────────────┐     ┌────────────┐              │
        │   │  Gamma API │────▶│  Market    │              │
        │   │  (discover)│     │  Filter    │              │
        │   └────────────┘     └─────┬──────┘              │
        │                            │                     │
        │   ┌────────────┐     ┌─────▼──────┐              │
        │   │ CLOB WS    │────▶│  Strategy  │              │
        │   │ (prices)   │     │  Evaluator │              │
        │   └────────────┘     └─────┬──────┘              │
        │                            │                     │
        │   ┌────────────┐     ┌─────▼──────┐              │
        │   │ Risk       │◀────│  Order     │              │
        │   │ Manager    │     │  Builder   │              │
        │   └─────┬──────┘     └─────┬──────┘              │
        │         │                  │                     │
        │         └──────────┬───────┘                     │
        │                    ▼                             │
        │            ┌───────────────┐                     │
        │            │  CLOB POST    │──▶ Polymarket       │
        │            │  /order       │                     │
        │            └───────────────┘                     │
        └──────────────────────────────────────────────────┘
```

The bot's main loop runs every `scan_interval` seconds:

1. **Fetch** active markets from the Gamma API
2. **Filter** by volume, spread, and category
3. **Subscribe** to live orderbook updates via WebSocket
4. **Evaluate** each strategy against the live state
5. **Validate** the trade with the Risk Manager (caps, drawdown, allowance)
6. **Sign** the order with EIP-712 and post it to the CLOB
7. **Track** the fill and update the position ledger

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/polymarket-bot.git
cd polymarket-bot

# 2. Install dependencies
pip install -e .

# 3. Configure credentials (see "Configuration" below)
cp .env.example .env
# edit .env with your Polygon private key + funder address

# 4. Run a dry-run with the built-in mean-reversion strategy
polymarket-bot run --strategy mean_reversion --dry-run

# 5. Go live (real orders!)
polymarket-bot run --strategy mean_reversion
```

That's it. The bot is now scanning Polymarket markets and printing every decision it makes.

## 📦 Installation

### Requirements

- Python **3.10 or newer**
- A Polygon wallet with **USDC (PoS)** for trading
- Either an **email/Magic-wallet** Polymarket account (signature_type=1, recommended) or a **MetaMask/EOA** wallet (signature_type=0, requires manual allowance approval)

### From PyPI (recommended once published)

```bash
pip install polymarket-bot
```

### From source

```bash
git clone https://github.com/YOUR-USERNAME/polymarket-bot.git
cd polymarket-bot
pip install -e ".[dev]"
```

### Using Docker

```bash
docker pull ghcr.io/YOUR-USERNAME/polymarket-bot:latest
docker run --env-file .env ghcr.io/YOUR-USERNAME/polymarket-bot:latest
```

## ⚙️ Configuration

All credentials live in `.env`. Copy `.env.example` and fill in the blanks:

```env
# Required
POLYMARKET_PRIVATE_KEY=0xabc...        # Your Polygon wallet private key
POLYMARKET_FUNDER_ADDRESS=0xdef...      # The address holding your USDC
POLYMARKET_SIGNATURE_TYPE=1             # 0=EOA/MetaMask, 1=Magic/Email, 2=Browser proxy

# Optional — auto-derived from private key if omitted
POLYMARKET_API_KEY=
POLYMARKET_API_SECRET=
POLYMARKET_API_PASSPHRASE=

# Endpoints (defaults shown)
POLYMARKET_CLOB_HOST=https://clob.polymarket.com
POLYMARKET_GAMMA_HOST=https://gamma-api.polymarket.com
POLYMARKET_DATA_HOST=https://data-api.polymarket.com
POLYMARKET_CHAIN_ID=137
```

Strategy parameters live in `config.yaml`:

```yaml
strategy:
  name: mean_reversion
  params:
    lower_bound: 0.05
    upper_bound: 0.30
    min_volume_usd: 50000
    max_spread: 0.03

risk:
  max_position_size_usd: 25
  max_open_positions: 5
  daily_loss_limit_usd: 100
  kill_switch_drawdown_pct: 20

execution:
  scan_interval_seconds: 30
  order_type: GTC          # GTC, FOK, GTD
  dry_run: false
```

## 📊 Trading Strategies

The bot ships with several reference strategies. Each lives in `src/polymarket_bot/strategies/` and inherits from `BaseStrategy`.

| Strategy | Description | Best for |
|---|---|---|
| `mean_reversion` | Buys oversold YES/NO shares (price < lower_bound) and exits at fair value | Long-tail political and crypto markets |
| `market_making` | Posts both sides of the book around the midpoint, earns the spread | High-volume liquid markets |
| `arbitrage` | Detects mispriced pairs across related markets (e.g., NegRisk events) | Multi-outcome events |
| `ml_signal` | Uses an external ML model (your own) to generate buy/sell signals | Quants with edge data |
| `momentum` | Follows price moves above a configurable Z-score | Breaking news markets |

### Writing your own strategy

```python
# src/polymarket_bot/strategies/my_strategy.py
from polymarket_bot.strategies.base import BaseStrategy, Signal

class MyStrategy(BaseStrategy):
    name = "my_strategy"

    def evaluate(self, market, orderbook, position) -> Signal | None:
        if orderbook.best_ask < 0.10 and market.volume_24h > 10_000:
            return Signal.buy(
                token_id=market.yes_token_id,
                price=orderbook.best_ask,
                size=10,
            )
        return None
```

Drop the file in the `strategies/` folder and run:

```bash
polymarket-bot run --strategy my_strategy
```

## 💡 Usage Examples

### List active markets

```bash
polymarket-bot markets list --sort-by volume --limit 10
```

### Inspect an orderbook

```bash
polymarket-bot orderbook --market-id 0xabc...
```

### Show open positions and P&L

```bash
polymarket-bot portfolio
```

### Backtest a strategy

```bash
polymarket-bot backtest --strategy mean_reversion --from 2026-01-01 --to 2026-04-01
```

### Place a one-off limit order

```bash
polymarket-bot order place \
  --token-id 71321... \
  --side BUY \
  --price 0.42 \
  --size 25
```

### As a Python library

```python
from polymarket_bot import PolymarketBot
from polymarket_bot.strategies import MeanReversionStrategy

bot = PolymarketBot.from_env()
bot.add_strategy(MeanReversionStrategy(lower=0.05, upper=0.30))
bot.run()
```

## 🏗️ Architecture

```
polymarket-bot/
├── src/polymarket_bot/
│   ├── __init__.py
│   ├── bot.py              # Main orchestrator
│   ├── cli.py              # Command-line interface (Typer)
│   ├── config.py           # Pydantic settings
│   ├── exchange/
│   │   ├── clob.py         # CLOB API wrapper (orders, fills)
│   │   ├── gamma.py        # Gamma API wrapper (market discovery)
│   │   ├── data.py         # Data API wrapper (positions, P&L)
│   │   └── websocket.py    # CLOB WebSocket client
│   ├── strategies/
│   │   ├── base.py         # Abstract base class
│   │   ├── mean_reversion.py
│   │   ├── market_making.py
│   │   ├── arbitrage.py
│   │   └── momentum.py
│   ├── risk/
│   │   ├── manager.py      # Pre-trade risk checks
│   │   └── kill_switch.py  # Emergency stop
│   └── utils/
│       ├── logging.py
│       └── metrics.py      # Prometheus exporters
├── tests/
├── examples/
├── docs/
├── Dockerfile
├── docker-compose.yml
└── config.yaml
```

The codebase follows strict layering: the strategy layer never touches HTTP, the CLI never touches the order signer. This makes it trivial to swap any layer (use a different exchange wrapper, plug in a different signer, etc.).

## 🛡️ Risk Management

> ⚠️ **Trading is risky. This bot can and will lose money. Never deploy capital you can't afford to lose.**

Built-in safeguards:

- **Position size cap** — no single order exceeds `max_position_size_usd`
- **Open position cap** — refuses new orders past `max_open_positions`
- **Daily loss limit** — auto-pauses trading after `daily_loss_limit_usd`
- **Drawdown kill-switch** — bot exits all positions on `kill_switch_drawdown_pct`
- **Allowance check** — verifies USDC and CTF allowances before each session
- **Stale orderbook detection** — rejects trades on books older than 5 seconds
- **Slippage guard** — limits slippage on market orders
- **Rate limit honoring** — backs off on 429 responses

## 🚀 Deployment

### Docker Compose (recommended)

```bash
docker compose up -d
```

Includes the bot, Prometheus, and a pre-built Grafana dashboard at `http://localhost:3000`.

### systemd on a VPS

A reference unit file is provided at `examples/polymarket-bot.service`.

```bash
sudo cp examples/polymarket-bot.service /etc/systemd/system/
sudo systemctl enable --now polymarket-bot
sudo journalctl -u polymarket-bot -f
```

For minimal latency to the Polymarket CLOB (hosted on AWS `eu-west-2`), pick a London, Dublin, or Amsterdam VPS. Round-trip latency from Dublin is under 5ms; from US East Coast it's around 130ms.

## ❓ FAQ

**Q: Is using a bot on Polymarket allowed?**
Yes. Polymarket exposes a public CLOB API specifically for programmatic trading. Many of the platform's most active traders use bots.

**Q: Does Polymarket have a testnet?**
No. All API calls hit production. Always start with $1–$5 position sizes when testing new logic.

**Q: How much capital do I need?**
The CLOB has a $1 minimum order. Realistically, $50–$200 lets you run multi-position strategies. The bot itself is free.

**Q: What are the fees?**
Makers pay 0%. Taker fees vary by category (crypto ~1.80%, sports 0.75%, politics 1.00%, geopolitics 0%). The bot's risk module accounts for this when computing expected value.

**Q: Can I run multiple strategies at once?**
Yes. Pass `--strategy s1,s2,s3` or list them in `config.yaml` under `strategies:`.

**Q: Will this bot make me money?**
That depends entirely on the strategy and your edge. The included strategies are reference implementations, not alpha. If they printed money out of the box, we wouldn't be giving them away.

**Q: Does it work with Polymarket US (the CFTC-regulated US version)?**
The Polymarket US API uses Ed25519 auth and lives at `api.polymarket.us`. Support is on the roadmap — see [#1](#).

**Q: What's the difference vs. `py-clob-client`?**
`py-clob-client` is the official low-level SDK. This project sits on top of it and adds market discovery, strategy framework, risk management, scheduling, logging, and a CLI.

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. Trading prediction markets involves substantial risk of loss. The authors and contributors are not responsible for any financial losses incurred by using this bot. **You** are responsible for understanding the strategies you deploy and complying with all applicable laws and Polymarket's Terms of Service. Polymarket may not be available in your jurisdiction.

This project is **not affiliated with, endorsed by, or sponsored by Polymarket**. "Polymarket" is a trademark of its respective owner.

## 🤝 Contributing

Contributions are welcome and encouraged! Whether it's a new strategy, a bug fix, a doc improvement, or a translation — open a PR.

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-strategy`)
3. Run `pre-commit install` and `pytest`
4. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Good first issues

- Add a new reference strategy
- Improve test coverage
- Translate the README to your language
- Build out the Grafana dashboard
- Write a tutorial blog post (we'll link to it)

## ⭐ Star History

If this project saves you time, please **star the repo** — it helps other Polymarket traders find it.

## 📚 Related Projects

- [`Polymarket/py-clob-client`](https://github.com/Polymarket/py-clob-client) — the official Python CLOB SDK this bot is built on
- [`Polymarket/py-clob-client-v2`](https://github.com/Polymarket/py-clob-client-v2) — newer v2 SDK
- [`Polymarket/agents`](https://github.com/Polymarket/agents) — official LLM-driven agent reference
- [Polymarket Docs](https://docs.polymarket.com/) — the canonical API reference

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

**Keywords:** polymarket, polymarket bot, polymarket trading bot, polymarket api, polymarket python, prediction market bot, prediction market trading, automated trading bot, crypto prediction market, CLOB API, py-clob-client, algorithmic trading, market making bot, arbitrage bot, polymarket automation, polygon trading bot, USDC trading bot, polymarket clob, polymarket gamma api, polymarket websocket.
