"""Logging utils."""

__all__ = [
    "InterceptHandler",
]


import contextlib
import logging
import sys

with contextlib.suppress(ImportError):
    from loguru import logger


class InterceptHandler(logging.Handler):
    """Standard logging handler to send logs to :mod:`loguru`.

    References:
        https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
