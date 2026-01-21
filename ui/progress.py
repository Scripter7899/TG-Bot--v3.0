"""
Progress Bar and Status Indicators for FULL-TG v3.0
"""

import sys
import time
from ui.colors import *

class ProgressBar:
    """Simple progress bar for terminal"""
    
    def __init__(self, total, prefix='Progress:', length=50):
        self.total = total
        self.prefix = prefix
        self.length = length
        self.current = 0
    
    def update(self, current=None):
        """Update progress bar"""
        if current is not None:
            self.current = current
        else:
            self.current += 1
        
        percent = self.current / self.total
        filled = int(self.length * percent)
        bar = '█' * filled + '░' * (self.length - filled)
        
        sys.stdout.write(f'\r{INFO}{self.prefix} |{bar}| {self.current}/{self.total} ({percent*100:.1f}%){RESET}')
        sys.stdout.flush()
        
        if self.current >= self.total:
            print()  # New line when complete
    
    def finish(self):
        """Complete the progress bar"""
        self.update(self.total)

class StatusIndicator:
    """Status indicator for operations"""
    
    @staticmethod
    def show_processing(message):
        """Show processing message"""
        print(f"{INFO}⏳ {message}...{RESET}")
    
    @staticmethod
    def show_success(message):
        """Show success message"""
        print(success(message))
    
    @staticmethod
    def show_error(message):
        """Show error message"""
        print(error(message))
    
    @staticmethod
    def show_warning(message):
        """Show warning message"""
        print(warning(message))
    
    @staticmethod
    def show_info(message):
        """Show info message"""
        print(info(message))

class Counter:
    """Real-time counter for operations"""
    
    def __init__(self, label="Count"):
        self.count = 0
        self.label = label
    
    def increment(self, message=""):
        """Increment and display counter"""
        self.count += 1
        if message:
            print(f"{SUCCESS}{self.label}: {self.count} - {message}{RESET}")
        else:
            sys.stdout.write(f'\r{INFO}{self.label}: {self.count}{RESET}')
            sys.stdout.flush()
    
    def get_count(self):
        """Get current count"""
        return self.count
    
    def reset(self):
        """Reset counter"""
        self.count = 0

def show_spinner(message, duration=2):
    """Show a spinner animation"""
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        sys.stdout.write(f'\r{INFO}{spinner[i % len(spinner)]} {message}...{RESET}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    
    sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
    sys.stdout.flush()
