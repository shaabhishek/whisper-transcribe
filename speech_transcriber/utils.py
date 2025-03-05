"""Utility functions for the speech transcriber application."""

import logging
from typing import Optional

# Configure the basic logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Silence external loggers
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("google.generativeai").setLevel(logging.WARNING)


class Logger:
    """Simple logger to wrap print statements and make them configurable."""

    # Default to enabled
    enabled = True

    @classmethod
    def info(cls, message: str) -> None:
        """Log an info message.

        Args:
            message: The message to log
        """
        if cls.enabled:
            logging.info(message)

    @classmethod
    def error(cls, message: str, exc: Optional[Exception] = None) -> None:
        """Log an error message.

        Args:
            message: The error message to log
            exc: Optional exception that caused the error
        """
        if cls.enabled:
            if exc:
                logging.error(f"{message}: {exc}")
            else:
                logging.error(message)

    @classmethod
    def warn(cls, message: str) -> None:
        """Log a warning message.

        Args:
            message: The warning message to log
        """
        if cls.enabled:
            logging.warning(message)

    @classmethod
    def set_enabled(cls, enabled: bool) -> None:
        """Enable or disable logging.

        Args:
            enabled: Whether logging should be enabled
        """
        cls.enabled = enabled


# Function to report file size
def report_file_size(file_size_bytes: int, service_name: str) -> None:
    """Report the size of a file being uploaded to a service.

    Args:
        file_size_bytes: Size of the file in bytes
        service_name: Name of the service the file is being uploaded to
    """
    file_size_kb = file_size_bytes / 1024
    file_size_mb = file_size_kb / 1024

    if file_size_mb >= 1:
        Logger.info(
            f"Uploading audio file ({file_size_mb:.2f} MB) to {service_name}..."
        )
    else:
        Logger.info(
            f"Uploading audio file ({file_size_kb:.2f} KB) to {service_name}..."
        )
