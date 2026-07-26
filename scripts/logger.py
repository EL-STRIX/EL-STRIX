"""Centralised logging configuration for EL-STRIX."""

import logging
import sys

# ──────────────────────────────────────────────
# Logger Setup
# ──────────────────────────────────────────────
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_logger(name: str = "EL-STRIX") -> logging.Logger:
    """Create and configure the application logger.

    Args:
        name: Logger name.

    Returns:
        Configured ``logging.Logger`` instance.
    """
    log = logging.getLogger(name)

    if log.handlers:
        return log

    log.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    log.addHandler(console_handler)
    return log


logger: logging.Logger = _build_logger()
