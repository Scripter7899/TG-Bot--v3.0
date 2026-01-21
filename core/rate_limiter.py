"""
Rate Limiter and Flood Control for FULL-TG v3.0
Prevents Telegram FloodWait errors
"""

import asyncio
import time
from collections import defaultdict
from telethon.errors import FloodWaitError
import config
from core.logger import logger

class RateLimiter:
    """Rate limiter for Telegram operations"""
    
    def __init__(self):
        self.last_action = defaultdict(float)
        self.flood_wait_until = defaultdict(float)
        self.action_counts = defaultdict(int)
    
    async def wait_if_needed(self, account_id, action_type='default'):
        """Wait if rate limit requires"""
        key = f"{account_id}_{action_type}"
        current_time = time.time()
        
        # Check if in flood wait
        if current_time < self.flood_wait_until[key]:
            wait_time = self.flood_wait_until[key] - current_time
            logger.warning(f"Account {account_id} in flood wait. Waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        # Check minimum delay
        if key in self.last_action:
            elapsed = current_time - self.last_action[key]
            if elapsed < config.DEFAULT_DELAY:
                wait_time = config.DEFAULT_DELAY - elapsed
                await asyncio.sleep(wait_time)
        
        self.last_action[key] = time.time()
        self.action_counts[key] += 1
    
    def set_flood_wait(self, account_id, action_type, wait_seconds):
        """Set flood wait time for account"""
        key = f"{account_id}_{action_type}"
        # Add multiplier for safety
        adjusted_wait = wait_seconds * config.FLOOD_WAIT_MULTIPLIER
        self.flood_wait_until[key] = time.time() + adjusted_wait
        logger.warning(f"Flood wait set for {key}: {adjusted_wait}s")
    
    def get_action_count(self, account_id, action_type='default'):
        """Get action count for account"""
        key = f"{account_id}_{action_type}"
        return self.action_counts.get(key, 0)
    
    def reset_counts(self):
        """Reset all action counts"""
        self.action_counts.clear()

# Global rate limiter
rate_limiter = RateLimiter()

async def handle_flood_wait(func, *args, **kwargs):
    """Decorator-like function to handle FloodWait errors"""
    retries = 0
    while retries < config.MAX_RETRIES:
        try:
            return await func(*args, **kwargs)
        except FloodWaitError as e:
            retries += 1
            wait_time = e.seconds * config.FLOOD_WAIT_MULTIPLIER
            logger.warning(f"FloodWait: {e.seconds}s. Waiting {wait_time}s (Retry {retries}/{config.MAX_RETRIES})")
            
            if retries >= config.MAX_RETRIES:
                logger.error(f"Max retries reached for {func.__name__}")
                raise
            
            await asyncio.sleep(wait_time)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    
    raise Exception(f"Failed after {config.MAX_RETRIES} retries")
