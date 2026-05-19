"""Structured logging helpers."""

from __future__ import annotations

import logging
import sys
from typing import Any


class JsonLikeFormatter(logging.Formatter):
    """Small dependency-free formatter that keeps logs easy to parse."""

    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)
        return str(base)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLikeFormatter())
    logging.basicConfig(level=level.upper(), handlers=[handler], force=True)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
