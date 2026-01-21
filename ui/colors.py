"""
Color Scheme and UI Constants for FULL-TG v3.0
"""

from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Category Colors
ACCOUNT_COLOR = Fore.YELLOW
PROXY_COLOR = Fore.CYAN
MULTI_ACCOUNT_COLOR = Fore.MAGENTA
SESSION_COLOR = Fore.BLUE
USER_COLOR = Fore.LIGHTYELLOW_EX
MESSAGE_COLOR = Fore.LIGHTMAGENTA_EX
GROUP_COLOR = Fore.GREEN
CHANNEL_COLOR = Fore.LIGHTBLUE_EX
STORY_COLOR = Fore.LIGHTGREEN_EX
REPORT_COLOR = Fore.RED
STATS_COLOR = Fore.LIGHTCYAN_EX
SPAM_COLOR = Fore.LIGHTMAGENTA_EX
MARKETING_COLOR = Fore.LIGHTBLUE_EX
UTILITIES_COLOR = Fore.WHITE
ADMIN_COLOR = Fore.LIGHTRED_EX
HEALTH_COLOR = Fore.LIGHTYELLOW_EX
ADVANCED_COLOR = Fore.LIGHTGREEN_EX

# Status Colors
SUCCESS = Fore.GREEN
ERROR = Fore.RED
WARNING = Fore.YELLOW
INFO = Fore.CYAN
PROMPT = Fore.LIGHTWHITE_EX

# Special Colors
HEADER = Fore.LIGHTMAGENTA_EX
BANNER = Fore.LIGHTCYAN_EX
MENU_TITLE = Fore.LIGHTMAGENTA_EX

# Emojis
EMOJI_ACCOUNT = "🔑"
EMOJI_PROXY = "🌐"
EMOJI_MULTI = "👥"
EMOJI_SESSION = "💾"
EMOJI_USER = "👤"
EMOJI_MESSAGE = "💬"
EMOJI_GROUP = "📢"
EMOJI_STORY = "📖"
EMOJI_REPORT = "🚫"
EMOJI_STATS = "📊"
EMOJI_SPAM = "💥"
EMOJI_MARKETING = "📈"
EMOJI_UTILITIES = "🔧"
EMOJI_ADMIN = "🔨"
EMOJI_HEALTH = "❤️"
EMOJI_ADVANCED = "⚡"
EMOJI_EXIT = "🚪"

# Icons
ICON_SUCCESS = "✓"
ICON_ERROR = "✗"
ICON_WARNING = "⚠"
ICON_INFO = "ℹ"
ICON_ARROW = "➤"
ICON_BULLET = "•"

# Styles
BOLD = Style.BRIGHT
DIM = Style.DIM
RESET = Style.RESET_ALL

def colored(text, color):
    """Return colored text"""
    return f"{color}{text}{RESET}"

def success(text):
    """Return success colored text"""
    return f"{SUCCESS}{ICON_SUCCESS} {text}{RESET}"

def error(text):
    """Return error colored text"""
    return f"{ERROR}{ICON_ERROR} {text}{RESET}"

def warning(text):
    """Return warning colored text"""
    return f"{WARNING}{ICON_WARNING} {text}{RESET}"

def info(text):
    """Return info colored text"""
    return f"{INFO}{ICON_INFO} {text}{RESET}"

def prompt(text):
    """Return prompt colored text"""
    return f"{PROMPT}{ICON_ARROW} {text}{RESET}"
