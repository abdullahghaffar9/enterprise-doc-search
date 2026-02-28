"""
Configure application-wide logging. Replace all print() with logger calls.
Outputs structured log lines with timestamp, level, module name, and message.
"""
from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
) -> None:
    """Configure root logger. Call once at app startup."""
    fmt = format_string or (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
