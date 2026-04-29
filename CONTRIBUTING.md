# Contributing to Polymarket Bot

Thanks for your interest in improving Polymarket Bot! Contributions of all sizes are welcome — from typo fixes to whole new strategies.

## How to contribute

1. **Fork** the repository.
2. **Create a feature branch** off `main`:
   ```bash
   git checkout -b feat/your-strategy
   ```
3. **Install dev dependencies**:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```
4. **Write code** + **tests**.
5. **Run the local quality gate**:
   ```bash
   ruff check src tests
   black src tests
   pytest
   ```
6. **Commit** with a [Conventional Commits](https://www.conventionalcommits.org/) message:
   ```
   feat(strategies): add VWAP momentum strategy
   fix(clob): retry on 429 with exponential backoff
   docs: clarify Magic-wallet signature_type setup
   ```
7. **Open a Pull Request** against `main`. The CI will run automatically.

## What we love

- 🎯 New reference strategies (please add tests)
- 🐛 Bug fixes with a regression test
- 📝 Docs, tutorials, translations of the README
- 🧪 Better backtesting & simulation utilities
- 🛡️ Risk-management improvements
- 🔌 Adapters for other prediction-market venues

## What we discourage

- PRs without tests (we will ask you to add them)
- Wholesale rewrites of working modules
- Anything that bypasses the Risk Manager
- Hardcoded credentials anywhere — ever

## Code style

- Black, line length 100
- Ruff for lint
- Type hints required for public APIs
- Docstrings: short, plain English, why over how

## Reporting security issues

Please do **not** open a public issue for security vulnerabilities. Instead, see [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
