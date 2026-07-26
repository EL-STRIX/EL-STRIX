"""Centralized, professional logging configuration."""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

from paths import PathManager
from constants import DEFAULT_LOG_LEVEL

# ANSI Color Codes
class Colors:
    DEBUG = "\033[90m"     # Gray
    INFO = "\033[92m"      # Green
    WARNING = "\033[93m"   # Yellow
    ERROR = "\033[91m"     # Red
    CRITICAL = "\033[1;91m" # Bold Red
    RESET = "\033[0m"      # Reset

class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors to console output."""
    
    COLORS = {
        logging.DEBUG: Colors.DEBUG,
        logging.INFO: Colors.INFO,
        logging.WARNING: Colors.WARNING,
        logging.ERROR: Colors.ERROR,
        logging.CRITICAL: Colors.CRITICAL
    }
    
    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelno, Colors.RESET)
        format_str = f"{Colors.DEBUG}%(asctime)s{Colors.RESET} [{log_color}%(levelname)s{Colors.RESET}] %(name)s — {log_color}%(message)s{Colors.RESET}"
        formatter = logging.Formatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(name: str = "EL-STRIX", debug_mode: bool = False) -> logging.Logger:
    """Initialize and configure the professional logger."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if setup is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()
        
    log_level = logging.DEBUG if debug_mode else getattr(logging, DEFAULT_LOG_LEVEL)
    logger.setLevel(log_level)
    
    # 1. Console Handler (Colored)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)
    
    # 2. File Handler (Plain Text, Rotating)
    try:
        PathManager.ensure_directories() # Ensure logs dir exists
        log_file = PathManager.GENERATED_LOGS_DIR / f"el-strix_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024, # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if file logging fails (e.g., permissions)
        console_handler.setLevel(logging.WARNING)
        logger.warning(f"Failed to initialize file logger: {e}")
        
    return logger

# Create the default instance
logger = setup_logger()
