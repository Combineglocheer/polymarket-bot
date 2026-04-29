"""Structured logging setup."""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(level: str = "INFO", json: bool = False) -> None:
    """Configure structlog + stdlib logging."""

    level_no = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level_no,
    )

    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    if json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level_no),
        cache_logger_on_first_use=True,
    )
