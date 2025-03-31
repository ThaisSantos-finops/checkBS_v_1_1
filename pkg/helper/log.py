from datetime import datetime
import logging
import os
import stat
from logging.handlers import RotatingFileHandler
import sys

def create_log_directory(directory):
    log_directory = os.path.join(directory, 'logs')
    os.makedirs(log_directory, exist_ok=True)
    os.chmod(log_directory, stat.S_IRWXU)
    return log_directory

def configure_logger(filename, console_output=False, level=logging.INFO):
    log_directory = create_log_directory(os.getcwd())
    log_filename = os.path.join(log_directory, f"{filename}-{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Config the logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # RotatingFileHandler to rotate logs
    file_handler = RotatingFileHandler(log_filename, maxBytes=10**6, backupCount=5)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(file_handler)

    # Add console output if console_output is True
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(console_handler)
    log_info(f"Logs will be saved in {log_directory}")

def setup_logger():
    """Configure the logging system."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(f'logs/{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setLevel(logging.INFO)

    # Create formatters
    console_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set formatters
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def log_debug(message: str) -> None:
    """Log a debug message."""
    logging.debug(message)

def log_info(message: str) -> None:
    """Log an info message."""
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_error(message: str) -> None:
    """Log an error message."""
    logging.error(message)

def log_fatal(message: str) -> None:
    """Log a fatal error message."""
    logging.fatal(message)