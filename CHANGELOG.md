# Changelog

All notable changes to this project will be documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- WebSocket streaming for live orderbook updates
- Polymarket US (CFTC) backend support
- Backtester replay mode

## [0.1.0] - 2026-04-29

### Added
- Initial public release
- Polymarket CLOB, Gamma, and Data API wrappers
- Pluggable strategy framework with `BaseStrategy`
- Built-in `mean_reversion` and `market_making` strategies
- Risk Manager with position caps, daily loss limit, and kill-switch
- Typer-based CLI: `polymarket-bot run`, `markets list`, `portfolio`, `order place`
- `Dockerfile` and `docker-compose.yml` with Prometheus + Grafana
- `pytest` test suite for strategies and risk
- GitHub Actions CI on Python 3.10/3.11/3.12
