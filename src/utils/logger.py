import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import config

_logger_initialized = False

def setup_logger():
    global _logger_initialized
    if _logger_initialized:
        return
        
    log_dir = config.LOGS_DIR
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
        
    log_file = log_dir / f"{config.APP_NAME.lower()}.log"
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File Handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    _logger_initialized = True

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
