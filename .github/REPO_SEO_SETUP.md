# GitHub Repository SEO Setup

This file contains the **exact** settings you need to apply to the GitHub repository to maximize discoverability. GitHub's search algorithm ranks on (in order of weight): **repository name**, **About description**, **topics**, then stars/forks/watchers.

These settings have been picked based on 2026 GitHub SEO best practices: stack at least 6 topic tags (max 20), put the primary keyword in the name AND first words of the About, keep the description in the 5-15-word sweet spot.

---

## 1. Repository name

```
polymarket-bot
```

✅ Already set if you cloned to that directory. Keep it as `polymarket-bot` — it's the primary keyword and the exact phrase people search.

## 2. About → Description

Paste this **exactly** into the "Description" field on the repo home page (Edit → top right):

```
Automated Polymarket trading bot in Python — multi-strategy, risk-managed, CLOB API.
```

(13 words, primary keyword first, three secondary keywords, action verb.)

## 3. About → Website

```
https://docs.polymarket.com/
```

(Or your own docs site once you have one. A non-empty website field signals legitimacy.)

## 4. About → Topics (tags)

Add **all 18 of these topics** in this order. The order matters — GitHub displays the first ~6 most prominently.

```
polymarket
polymarket-bot
polymarket-api
trading-bot
prediction-market
prediction-markets
automated-trading
algorithmic-trading
crypto-trading-bot
clob
py-clob-client
polygon
python
market-making
arbitrage
quantitative-trading
defi
web3
```

How to add: Repo home → click ⚙️ next to "About" → paste each topic, press Enter between each.

## 5. README badges

Already in place. Once the repo is live, replace `YOUR-USERNAME` in all URLs with your real GitHub username so badges resolve.

## 6. Initial commit message

```
feat: initial public release of polymarket-bot v0.1.0

- CLOB / Gamma / Data API wrappers
- mean_reversion + market_making strategies
- Risk manager with position caps and kill-switch
- Typer CLI, Docker, systemd unit
- pytest suite, GitHub Actions CI
```

## 7. After pushing

- [ ] **Set topics** as listed above
- [ ] **Set description** as listed above
- [ ] **Pin** this repo on your profile
- [ ] **Add a social preview image** (Settings → General → Social preview) — repos with a custom OG image get materially more click-throughs from Google
- [ ] Enable **Issues** and **Discussions**
- [ ] Submit the repo to **Awesome Polymarket** lists (search GitHub for them)
- [ ] Post a launch thread on **r/polymarket**, **HN Show HN**, **Twitter/X**, **dev.to**
- [ ] Once you have ≥10 stars, the repo will start appearing in topic feeds

## 8. Why this works

Per studies of GitHub search: stars correlate ~0.93 with rank, but on-page metadata (name, about, topics) lets a 200-star repo outrank a 5,000-star repo for the exact-match query. We have:

- **Exact keyword in repo name** ✅
- **Keyword in first three words of description** ✅
- **18 topics** stacked (the sweet spot is 6–20) ✅
- **README headings include the keyword** ✅
- **Multiple keyword variants** in README (polymarket bot, polymarket trading bot, polymarket python bot, polymarket api bot, prediction market bot) ✅
- **Working code** — GitHub indexes file contents, and the keyword appears in module names, docstrings, CLI help ✅
- **License + Contributing + CoC + Security** — signals "real project" to search ranking ✅
- **CI passing badge** — signals active maintenance ✅
