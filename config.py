"""
Configuration Management for FULL-TG v3.0
Handles all application settings and environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"
CLONES_DIR = SESSIONS_DIR / "clones"

# Create directories if they don't exist
for directory in [SESSIONS_DIR, LOGS_DIR, DATA_DIR, EXPORTS_DIR, BACKUPS_DIR, CLONES_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Telegram API Configuration
API_ID = os.getenv("API_ID", "")
API_HASH = os.getenv("API_HASH", "")

# Convert API_ID to int if it's set
if API_ID and API_ID != "your_api_id_here":
    try:
        API_ID = int(API_ID)
    except ValueError:
        API_ID = ""

# Database Configuration
DATABASE_PATH = DATA_DIR / "database.db"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "True").lower() == "true"
LOG_ROTATION_SIZE = int(os.getenv("LOG_ROTATION_SIZE", "10485760"))  # 10MB

# Log Files
OPERATIONS_LOG = LOGS_DIR / "operations.log"
ERRORS_LOG = LOGS_DIR / "errors.log"
ADDED_USERS_LOG = LOGS_DIR / "added_users.log"
ERROR_USERS_LOG = LOGS_DIR / "error_users.log"
REMOVED_ACCOUNTS_LOG = LOGS_DIR / "removed_accounts.log"

# Rate Limiting Configuration
DEFAULT_DELAY = int(os.getenv("DEFAULT_DELAY", "2"))
FLOOD_WAIT_MULTIPLIER = float(os.getenv("FLOOD_WAIT_MULTIPLIER", "1.5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Invite Settings
INVITE_DELAY_MIN = 30
INVITE_DELAY_MAX = 60
INVITE_BATCH_SIZE = 50

# Message Settings
MESSAGE_DELAY_MIN = 2
MESSAGE_DELAY_MAX = 5

# Proxy Configuration
ENABLE_PROXY = os.getenv("ENABLE_PROXY", "False").lower() == "true"
DEFAULT_PROXY_TYPE = os.getenv("DEFAULT_PROXY_TYPE", "SOCKS5")

# Security Configuration
ENCRYPT_SESSIONS = os.getenv("ENCRYPT_SESSIONS", "True").lower() == "true"
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))

# Feature Flags
AUTO_HEALTH_CHECK = os.getenv("AUTO_HEALTH_CHECK", "True").lower() == "true"
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "3600"))

# Auto-React Configuration
# Add your target channels here (public usernames or private invite links)
# Loaded from .env (comma separated)
_channels_env = os.getenv("AUTO_REACT_CHANNELS", "")
AUTO_REACT_CHANNELS = [ch.strip() for ch in _channels_env.split(",") if ch.strip()]

# Application Info
APP_NAME = "FULL-TG"
APP_VERSION = "3.0"
APP_AUTHORS = "@MR_DIAZZZ"

# Validation
def validate_config():
    """Validate critical configuration"""
    errors = []
    
    if not API_ID or API_ID == "your_api_id_here" or API_ID == "":
        errors.append("API_ID is not set. Please configure .env file")
    
    if not API_HASH or API_HASH == "your_api_hash_here" or API_HASH == "":
        errors.append("API_HASH is not set. Please configure .env file")
    
    # Check if API_ID is valid integer
    if API_ID and not isinstance(API_ID, int):
        errors.append("API_ID must be a valid integer")
    
    if errors:
        return False, errors
    
    return True, []

# Export all settings
__all__ = [
    'BASE_DIR', 'SESSIONS_DIR', 'LOGS_DIR', 'DATA_DIR', 'EXPORTS_DIR', 'BACKUPS_DIR', 'CLONES_DIR',
    'API_ID', 'API_HASH', 'DATABASE_PATH', 'LOG_LEVEL', 'LOG_TO_FILE',
    'OPERATIONS_LOG', 'ERRORS_LOG', 'ADDED_USERS_LOG', 'ERROR_USERS_LOG', 'REMOVED_ACCOUNTS_LOG',
    'DEFAULT_DELAY', 'FLOOD_WAIT_MULTIPLIER', 'MAX_RETRIES',
    'INVITE_DELAY_MIN', 'INVITE_DELAY_MAX', 'INVITE_BATCH_SIZE',
    'MESSAGE_DELAY_MIN', 'MESSAGE_DELAY_MAX',
    'ENABLE_PROXY', 'DEFAULT_PROXY_TYPE',
    'ENCRYPT_SESSIONS', 'SESSION_TIMEOUT',
    'AUTO_HEALTH_CHECK', 'HEALTH_CHECK_INTERVAL',
    'APP_NAME', 'APP_VERSION', 'APP_AUTHORS',
    'validate_config'
]
