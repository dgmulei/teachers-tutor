"""
Logging utilities for the AI Teaching Assistant Platform.
"""

import logging
import sys
import streamlit as st
from typing import Optional


def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (default: INFO)

    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger("ai_teaching_assistant")
    logger.setLevel(log_level)

    # Create console handler and set level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to console handler
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    return logger


def configure_streamlit_logging() -> None:
    """
    Configure Streamlit's logging to use our custom logger.
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Remove existing handlers
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # Set up our custom logger
    logger = setup_logging()

    # Add our logger to the root logger
    root_logger.addHandler(logger.handlers[0])
    root_logger.setLevel(logger.level)


def log_error(error: Exception, message: Optional[str] = None) -> None:
    """
    Log an error and display it in the Streamlit UI.

    Args:
        error: Exception to log
        message: Optional custom error message
    """
    error_message = message or str(error)
    logging.error(f"Error: {error_message}", exc_info=True)
    st.error(error_message)
