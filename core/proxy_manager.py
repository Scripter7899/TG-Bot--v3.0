"""
Proxy Manager for FULL-TG v3.0
Handles proxy rotation and validation
"""

import asyncio
import aiohttp
from python_socks import ProxyType
import config
from core.database import db
from core.logger import logger

class ProxyManager:
    """Manages proxies for Telegram connections"""
    
    def __init__(self):
        self.proxies = []
        self.current_index = 0
    
    async def load_proxies(self):
        """Load proxies from database"""
        try:
            proxies = await db.get_all_proxies()
            self.proxies = []
            
            for proxy in proxies:
                proxy_dict = {
                    'id': proxy[0],
                    'type': proxy[1],
                    'addr': proxy[2],
                    'port': proxy[3],
                    'username': proxy[4],
                    'password': proxy[5],
                    'status': proxy[6]
                }
                self.proxies.append(proxy_dict)
            
            logger.info(f"Loaded {len(self.proxies)} proxies")
        except Exception as e:
            logger.error(f"Failed to load proxies: {e}")
    
    async def add_proxy(self, proxy_type, address, port, username=None, password=None):
        """Add new proxy"""
        try:
            # Validate proxy first
            is_valid = await self.validate_proxy(proxy_type, address, port, username, password)
            
            if not is_valid:
                logger.error("Proxy validation failed")
                return False
            
            # Add to database
            proxy_id = await db.add_proxy(proxy_type, address, port, username, password)
            
            if proxy_id:
                self.proxies.append({
                    'id': proxy_id,
                    'type': proxy_type,
                    'addr': address,
                    'port': port,
                    'username': username,
                    'password': password,
                    'status': 'active'
                })
                logger.success(f"Proxy added: {address}:{port}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to add proxy: {e}")
            return False
    
    async def validate_proxy(self, proxy_type, address, port, username=None, password=None):
        """Validate proxy by testing connection"""
        try:
            # Build proxy URL
            if username and password:
                proxy_url = f"{proxy_type.lower()}://{username}:{password}@{address}:{port}"
            else:
                proxy_url = f"{proxy_type.lower()}://{address}:{port}"
            
            # Test connection
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://api.telegram.org',
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200 or response.status == 404  # 404 is ok for telegram
        except Exception as e:
            logger.error(f"Proxy validation failed: {e}")
            return False
    
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        return self._format_proxy(proxy)
    
    def get_proxy_by_id(self, proxy_id):
        """Get specific proxy by ID"""
        for proxy in self.proxies:
            if proxy['id'] == proxy_id:
                return self._format_proxy(proxy)
        return None
    
    def _format_proxy(self, proxy):
        """Format proxy for Telethon"""
        if not proxy:
            return None
        
        # Map proxy type
        type_map = {
            'SOCKS5': ProxyType.SOCKS5,
            'SOCKS4': ProxyType.SOCKS4,
            'HTTP': ProxyType.HTTP
        }
        
        return {
            'proxy_type': type_map.get(proxy['type'], ProxyType.SOCKS5),
            'addr': proxy['addr'],
            'port': proxy['port'],
            'username': proxy['username'],
            'password': proxy['password'],
            'rdns': True
        }
    
    async def update_proxy_stats(self, proxy_id, success=True):
        """Update proxy statistics"""
        await db.update_proxy_stats(proxy_id, success)
    
    def get_all_proxies(self):
        """Get all proxies"""
        return self.proxies
    
    def get_proxy_count(self):
        """Get total proxy count"""
        return len(self.proxies)

# Global proxy manager
proxy_manager = ProxyManager()
