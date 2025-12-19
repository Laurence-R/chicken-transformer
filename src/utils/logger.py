"""Logging configuration for Fitness Dice Game.

Provides console and file logging with configurable levels and formats.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


# Log format with timestamp, level, module, and message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str = "chicken-transformer",
    level: int = logging.INFO,
    log_file: str = "logs/app.log",
    console: bool = True,
    file_logging: bool = True
) -> logging.Logger:
    """Setup logger with console and file handlers.
    
    Args:
        name: Logger name
        level: Logging level (logging.DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        console: Enable console output
        file_logging: Enable file logging
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logger(level=logging.DEBUG)
        >>> logger.info("Application started")
        >>> logger.debug("Debug information")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_logging:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance by name.
    
    Args:
        name: Logger name (typically module name)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing frame")
    """
    return logging.getLogger(name)


# Performance metrics logger (separate from application logs)
def setup_metrics_logger(log_file: str = "logs/metrics.log") -> logging.Logger:
    """Setup logger specifically for performance metrics.
    
    Args:
        log_file: Path to metrics log file
        
    Returns:
        Metrics logger instance
        
    Usage:
        >>> metrics_logger = setup_metrics_logger()
        >>> metrics_logger.info("inference_time_ms=45.2 fps=22.3")
    """
    logger = logging.getLogger("metrics")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler only (no console spam)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=50 * 1024 * 1024,  # 50MB for metrics
        backupCount=3,
        encoding='utf-8'
    )
    
    # Simplified format for metrics
    metrics_format = logging.Formatter("%(asctime)s | %(message)s", datefmt=DATE_FORMAT)
    file_handler.setFormatter(metrics_format)
    logger.addHandler(file_handler)
    
    return logger


# Default logger for convenience
default_logger = setup_logger()
