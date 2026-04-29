# Quickstart — Run your first Polymarket bot in 5 minutes

This guide walks you from a clean machine to a running bot. Total time: ~5 minutes.

## Step 1 — Install

```bash
git clone https://github.com/YOUR-USERNAME/polymarket-bot.git
cd polymarket-bot
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Step 2 — Get your credentials

You need two pieces of information:

1. **Your Polygon wallet's private key.** If you signed up for Polymarket with email, export your Magic wallet's private key from your Polymarket settings.
2. **Your Polymarket funder address.** This is the address shown on your Polymarket profile. It's the address that *holds* your USDC, which is different from the address that signs orders if you're using a Magic wallet.

> ⚠️ **Use a dedicated trading wallet.** Don't point the bot at the wallet that holds the rest of your crypto.

## Step 3 — Configure

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
POLYMARKET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
POLYMARKET_FUNDER_ADDRESS=0xYOUR_POLYMARKET_PROFILE_ADDRESS
POLYMARKET_SIGNATURE_TYPE=1
```

`signature_type=1` is correct for the email/Magic wallet flow most users have.

## Step 4 — Verify it can read

```bash
polymarket-bot markets list --limit 5
```

You should see a table of the top 5 markets by volume. If this works, your read-side is good.

```bash
polymarket-bot portfolio
```

This should print your current Polymarket positions (or an empty table).

## Step 5 — Dry-run

Open `config.yaml` and make sure `execution.dry_run: true` is set. Then:

```bash
polymarket-bot run
```

The bot will scan markets, evaluate the configured strategy, and *log* every order it would have placed without actually sending anything.

## Step 6 — Go live

When you're comfortable with what the bot is doing in dry-run, flip `execution.dry_run: false` (or pass `--dry-run` to disable, omit it to enable).

Start small. Keep your `risk.max_position_size_usd` low (e.g., $1–$5) and watch the bot for at least a full day before scaling up.

## What's next?

- [Writing custom strategies →](strategies.md)
- [Deploying to a VPS →](deployment.md)
- [Backtesting →](backtesting.md)
