# syntax=docker/dockerfile:1.6
# =============================================================================
# Polymarket Bot — Production image
# =============================================================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Build deps for cryptography / web3
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --upgrade pip && pip install --prefix=/install .

# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:${PATH}"

# non-root user
RUN groupadd -r bot && useradd --no-log-init -r -g bot bot
WORKDIR /home/bot

COPY --from=builder /install /usr/local
COPY --chown=bot:bot config.yaml ./

USER bot

EXPOSE 9090

ENTRYPOINT ["polymarket-bot"]
CMD ["run", "--config", "/home/bot/config.yaml"]
