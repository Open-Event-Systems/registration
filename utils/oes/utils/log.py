"""Logging module."""

import inspect
import logging
import sys

from loguru import logger

__all__ = [
    "setup_logging",
]


def setup_logging(debug: bool = False):
    """Set up logging."""
    logger.remove()
    logger.add(sys.stderr, level=logging.DEBUG if debug else logging.INFO)
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
