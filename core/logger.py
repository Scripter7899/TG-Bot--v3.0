"""
Comprehensive Logging System for FULL-TG v3.0
Handles console and file logging with rotation
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init
import config

# Initialize colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    FORMATS = {
        logging.DEBUG: f"{Style.DIM}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
        logging.INFO: f"{Fore.CYAN}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
        logging.WARNING: f"{Fore.YELLOW}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
        logging.ERROR: f"{Fore.RED}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
        logging.CRITICAL: f"{Fore.RED}{Style.BRIGHT}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

class Logger:
    """Main logger class"""
    
    def __init__(self, name="FULL-TG"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # File handlers if enabled
        if config.LOG_TO_FILE:
            self._setup_file_handlers()
    
    def _setup_file_handlers(self):
        """Setup rotating file handlers"""
        # Operations log
        operations_handler = RotatingFileHandler(
            config.OPERATIONS_LOG,
            maxBytes=config.LOG_ROTATION_SIZE,
            backupCount=5,
            encoding='utf-8'
        )
        operations_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(operations_handler)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
        self._log_to_error_file(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
        self._log_to_error_file(message)
    
    def success(self, message):
        """Log success message (custom level)"""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        self.logger.info(f"SUCCESS: {message}")
    
    def _log_to_error_file(self, message):
        """Log errors to separate error file"""
        try:
            with open(config.ERRORS_LOG, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass
    
    def log_operation(self, operation, details, status="SUCCESS"):
        """Log operation to operations log"""
        message = f"{operation} | {details} | Status: {status}"
        if status == "SUCCESS":
            self.success(message)
        elif status == "ERROR":
            self.error(message)
        else:
            self.info(message)
    
    def log_added_user(self, username, user_id, group):
        """Log successfully added user"""
        try:
            with open(config.ADDED_USERS_LOG, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] Added: @{username} (ID: {user_id}) to {group}\n")
        except Exception as e:
            self.error(f"Failed to log added user: {e}")
    
    def log_error_user(self, username, user_id, group, reason):
        """Log failed user addition"""
        try:
            with open(config.ERROR_USERS_LOG, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] Failed: @{username} (ID: {user_id}) to {group} - Reason: {reason}\n")
        except Exception as e:
            self.error(f"Failed to log error user: {e}")
    
    def log_removed_account(self, phone, reason):
        """Log removed account"""
        try:
            with open(config.REMOVED_ACCOUNTS_LOG, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] Removed: {phone} - Reason: {reason}\n")
        except Exception as e:
            self.error(f"Failed to log removed account: {e}")

# Global logger instance
logger = Logger()

# Export logger functions
def debug(msg): logger.debug(msg)
def info(msg): logger.info(msg)
def warning(msg): logger.warning(msg)
def error(msg): logger.error(msg)
def critical(msg): logger.critical(msg)
def success(msg): logger.success(msg)
def log_operation(op, details, status="SUCCESS"): logger.log_operation(op, details, status)
def log_added_user(username, user_id, group): logger.log_added_user(username, user_id, group)
def log_error_user(username, user_id, group, reason): logger.log_error_user(username, user_id, group, reason)
def log_removed_account(phone, reason): logger.log_removed_account(phone, reason)
