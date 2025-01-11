# utils/logger.py

import logging
from utils.config import LOGS_FILE


class Color:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BRIGHT_RED = "\033[91m"


# ! Set desired console level (DEBUG or INFO)
LOG_LEVEL = logging.INFO
# LOG_LEVEL = logging.DEBUG

# Root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # Ensures all messages are processed

# Clear any existing handlers to prevent duplicate logs
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# File handler (always includes line numbers)
file_handler = logging.FileHandler(LOGS_FILE)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d): %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(file_formatter)

# Console handler (conditional formatting based on LOG_LEVEL)
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)


# Formatter with color for console output
class ColorFormatter(logging.Formatter):
    # Define colors for each log level using ANSI codes
    COLORS = {
        logging.DEBUG: Color.CYAN,
        logging.INFO: Color.GREEN,
        logging.WARNING: Color.YELLOW,
        logging.ERROR: Color.RED,
        logging.CRITICAL: Color.BRIGHT_RED,
    }

    def format(self, record):
        # Color the levelname only
        log_color = self.COLORS.get(record.levelno, Color.RESET)
        levelname_colored = f"{log_color}{record.levelname}{Color.RESET}"
        record.levelname = levelname_colored  # Replace levelname with colored version

        # Return the formatted message
        return super().format(record)


# Select formatter based on LOG_LEVEL
if LOG_LEVEL == logging.DEBUG:
    # Console format with filename and line number in DEBUG mode
    console_formatter = ColorFormatter(
        "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
else:
    # Console format without line number in INFO mode
    console_formatter = ColorFormatter(
        "%(asctime)s [%(levelname)s] (%(filename)s): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

console_handler.setFormatter(console_formatter)

# Add handlers to the root logger
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)