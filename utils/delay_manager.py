"""
Smart Delay Manager
Provides human-like random delays for all operations
"""

import random
import asyncio
from typing import Tuple
from core.logger import logger

class DelayManager:
    """Manage smart delays for anti-ban"""
    
    # Delay ranges in seconds (min, max)
    DELAYS = {
        'invite': (60, 180),        # 1-3 minutes
        'broadcast': (40, 180),     # 40s-3 minutes
        'join': (60, 240),          # 1-4 minutes
        'react': (5, 10),           # 5-10 seconds (light action)
        'post': (120, 300),         # 2-5 minutes
        'comment': (60, 180),       # 1-3 minutes
        'message': (40, 120),       # 40s-2 minutes
        'bio_update': (30, 60),     # 30s-1 minute
        'default': (60, 300)        # 1-5 minutes
    }
    
    @staticmethod
    def get_delay(action_type: str = 'default') -> int:
        """Get random delay for action type"""
        delay_range = DelayManager.DELAYS.get(action_type, DelayManager.DELAYS['default'])
        delay = random.randint(delay_range[0], delay_range[1])
        return delay
    
    @staticmethod
    async def wait(action_type: str = 'default', custom_range: Tuple[int, int] = None):
        """Wait with random delay"""
        if custom_range:
            delay = random.randint(custom_range[0], custom_range[1])
        else:
            delay = DelayManager.get_delay(action_type)
        
        logger.debug(f"Waiting {delay} seconds ({action_type})")
        await asyncio.sleep(delay)
    
    @staticmethod
    def get_delay_range(action_type: str = 'default') -> Tuple[int, int]:
        """Get delay range for action type"""
        return DelayManager.DELAYS.get(action_type, DelayManager.DELAYS['default'])
    
    @staticmethod
    async def wait_with_progress(action_type: str, message: str = "Waiting"):
        """Wait with progress indicator"""
        delay = DelayManager.get_delay(action_type)
        logger.info(f"{message} for {delay} seconds...")
        await asyncio.sleep(delay)
