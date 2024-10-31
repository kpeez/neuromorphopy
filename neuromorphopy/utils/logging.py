"""Logging configuration for neuromorphopy."""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_to_file: bool = False,
    output_dir: Path | None = None,
    query_file: Path | None = None,
) -> None:
    """Configure logging for the application."""
    logger = logging.getLogger("neuromorphopy")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers.clear()

    verbose_fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    simple_fmt = logging.Formatter("%(message)s")
    if not quiet:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(simple_fmt)
        console.setLevel(logging.DEBUG if verbose else logging.WARNING)
        logger.addHandler(console)
    if log_to_file and output_dir and query_file:
        output_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d-%H_%M")
        query_name = query_file.stem
        log_filename = f"{date_str}-{query_name}.log"
        log_path = output_dir / log_filename

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(verbose_fmt)
        # Always show detailed logs in file
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        logger.debug(f"Logging to file: {log_path}")

def get_logger() -> logging.Logger:
    """Get the neuromorphopy logger."""
    return logging.getLogger("neuromorphopy")
