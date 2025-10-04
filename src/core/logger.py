import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        result = super().format(record)
        
        # Reset levelname to avoid side effects
        record.levelname = levelname
        
        return result


def get_logger(
    name: str,
    level: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    Get or create a logger with the specified name.
    
    Args:
        name: Name of the logger (usually module or component name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, reads from LOG_LEVEL environment variable or defaults to INFO
        use_colors: Whether to use colored output (default: True)
    
    Returns:
        Configured logger instance
    """
    import os
    
    # Get the logger
    logger = logging.getLogger(name)
    
    # Only configure if no handlers exist (avoid duplicate handlers)
    if not logger.handlers:
        # Determine log level
        if level is None:
            level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        log_level = getattr(logging, level, logging.INFO)
        logger.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Create formatter
        if use_colors:
            formatter = ColoredFormatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger


def configure_root_logger(level: str = 'INFO', use_colors: bool = True):
    """
    Configure the root logger for the entire application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_colors: Whether to use colored output (default: True)
    """
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    if use_colors:
        formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

