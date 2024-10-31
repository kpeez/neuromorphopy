"""Logging configuration for neuromorphopy."""

import logging
import sys
from pathlib import Path
from typing import TextIO


def setup_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: Path | str | None = None,
    stream: TextIO | None = None,
) -> None:
    """Configure logging for the application.

    Args:
        verbose: Enable debug logging
        quiet: Disable all output except errors
        log_file: Optional file to write logs to
        stream: Optional stream to write logs to (defaults to sys.stdout)
    """

    logger = logging.getLogger("neuromorphopy")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers.clear()
    verbose_fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    simple_fmt = logging.Formatter("%(message)s")
    if not quiet:
        console = logging.StreamHandler(stream or sys.stdout)
        console.setFormatter(verbose_fmt if verbose else simple_fmt)
        console.setLevel(logging.DEBUG if verbose else logging.INFO)
        logger.addHandler(console)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(verbose_fmt)
        file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        logger.addHandler(file_handler)

def get_logger() -> logging.Logger:
    """Get the neuromorphopy logger."""
    return logging.getLogger("neuromorphopy")
