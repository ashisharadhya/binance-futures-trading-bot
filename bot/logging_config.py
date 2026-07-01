"""
logging_config.py

Central logging setup for the trading bot.

All API requests, responses, and errors are logged to a rotating file
(trading_bot.log) AND to the console (INFO level and above on console,
DEBUG level and above in the file).
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "trading_bot.log"


def setup_logging(name: str = "trading_bot") -> logging.Logger:
    """
    Configure and return the application logger.

    - File handler: DEBUG level, rotates at 2MB, keeps 3 backups.
    - Console handler: INFO level, concise output for the user.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if setup_logging() is called more than once
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
