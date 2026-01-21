"""
Utility for parsing CSV and text files
Handles username lists, group lists, and data imports
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional
from core.logger import logger

class FileParser:
    """Parse various file formats for bulk operations"""
    
    @staticmethod
    def parse_usernames_csv(file_path: str) -> List[str]:
        """
        Parse usernames from CSV file
        Supports formats: @username, username, +phone
        """
        try:
            usernames = []
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return []
            
            # Try reading as plain text first (one username per line)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):  # Skip empty lines and comments
                        continue
                    
                    # Clean username
                    username = line.replace('@', '').strip()
                    if username:
                        usernames.append(username)
            
            logger.info(f"Parsed {len(usernames)} usernames from {file_path}")
            return usernames
            
        except Exception as e:
            logger.error(f"Failed to parse usernames: {e}")
            return []
    
    @staticmethod
    def parse_groups_file(file_path: str) -> List[str]:
        """
        Parse group URLs/usernames from text file
        Supports: https://t.me/group, @group, t.me/joinchat/xxx
        """
        try:
            groups = []
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return []
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Extract group identifier
                    if 'joinchat' in line:
                        groups.append(line)  # Full invite link
                    elif 't.me/' in line:
                        # Extract username from URL
                        parts = line.split('t.me/')
                        if len(parts) > 1:
                            username = parts[1].split('/')[0].replace('@', '')
                            groups.append(username)
                    elif line.startswith('@'):
                        groups.append(line[1:])  # Remove @
                    else:
                        groups.append(line)
            
            logger.info(f"Parsed {len(groups)} groups from {file_path}")
            return groups
            
        except Exception as e:
            logger.error(f"Failed to parse groups: {e}")
            return []
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        
        # Remove @ if present
        username = username.replace('@', '')
        
        # Check length (5-32 characters for Telegram)
        if len(username) < 5 or len(username) > 32:
            return False
        
        # Check valid characters (letters, numbers, underscores)
        if not username.replace('_', '').isalnum():
            return False
        
        return True
    
    @staticmethod
    def parse_channel_post_url(url: str) -> Optional[Dict[str, any]]:
        """
        Parse Telegram channel post URL
        Returns: {channel: str, message_id: int}
        """
        try:
            # Format: https://t.me/channel/123 or https://t.me/c/123456/789
            if 't.me/' not in url:
                return None
            
            parts = url.split('t.me/')
            if len(parts) < 2:
                return None
            
            path = parts[1].strip('/')
            segments = path.split('/')
            
            if len(segments) < 2:
                return None
            
            # Public channel: t.me/channel/123
            if segments[0] != 'c':
                channel = segments[0]
                message_id = int(segments[1])
                return {'channel': channel, 'message_id': message_id, 'is_private': False}
            
            # Private channel: t.me/c/123456/789
            else:
                channel_id = int(segments[1])
                message_id = int(segments[2])
                return {'channel': channel_id, 'message_id': message_id, 'is_private': True}
                
        except Exception as e:
            logger.error(f"Failed to parse channel URL: {e}")
            return None
