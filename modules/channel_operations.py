"""
Channel Operations Module
Join channels with all accounts (public and private)
"""

import asyncio
import random
import re
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import FloodWaitError, ChannelPrivateError, InviteHashExpiredError
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator
from utils.delay_manager import DelayManager

status = StatusIndicator()

def extract_invite_hash(url):
    """Extract invite hash from Telegram invite link"""
    # Patterns: https://t.me/+xxxxx or https://t.me/joinchat/xxxxx
    patterns = [
        r't\.me/\+([A-Za-z0-9_-]+)',
        r't\.me/joinchat/([A-Za-z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

async def join_channels_all_accounts():
    """
    Feature 124 (NEW): Join channels with all accounts
    Supports both public and private channels
    """
    try:
        print(f"\n{'='*70}")
        print("⭐ JOIN CHANNELS [ALL ACCOUNTS]")
        print(f"{'='*70}\n")
        
        print("Channel URL Options:")
        print("1. Public channel (e.g., https://t.me/channelname or @channelname)")
        print("2. Private channel (e.g., https://t.me/+xxxxx or t.me/joinchat/xxxxx)")
        print()
        
        # Get channel URL
        channel_url = input("Enter channel URL or username: ").strip()
        
        if not channel_url:
            status.show_error("Channel URL cannot be empty")
            return
        
        # Determine if it's an invite link or public channel
        invite_hash = extract_invite_hash(channel_url)
        is_invite_link = invite_hash is not None
        
        # Get all accounts
        clients_dict = await session_manager.get_all_clients()
        
        if not clients_dict:
            status.show_error("No active accounts found")
            return
        
        print(f"\n{'-'*70}")
        print(f"Channel: {channel_url}")
        print(f"Type: {'Private Invite Link' if is_invite_link else 'Public Channel'}")
        print(f"Accounts: {len(clients_dict)}")
        print(f"Mode: PARALLEL (all accounts work simultaneously)")
        print(f"Delay: 60-240 seconds per account")
        print(f"{'-'*70}\n")
        
        confirm = input("Start joining? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        # Join function for single account
        async def join_for_account(phone, client):
            """Join channel for a single account"""
            try:
                logger.info(f"[{phone}] Starting to join channel")
                
                # Reconnect if needed
                if not client.is_connected():
                    await client.connect()
                
                # Check if already a member (for public channels only)
                if not is_invite_link:
                    try:
                        entity = await client.get_entity(channel_url)
                        # Try to check if we're already a participant
                        try:
                            me = await client.get_me()
                            participants = await client.get_participants(entity, limit=1, search=me.username if me.username else str(me.id))
                            if len(participants) > 0:
                                logger.info(f"[{phone}] Already a member of this channel")
                                return True
                        except Exception:
                            pass  # Can't check, proceed to join
                    except Exception:
                        pass  # Can't get entity, proceed to join
                
                # Join based on type
                if is_invite_link:
                    # Private channel - use invite hash
                    try:
                        await client(ImportChatInviteRequest(invite_hash))
                        logger.success(f"[{phone}] Successfully joined via invite link")
                    except Exception as e:
                        if "already" in str(e).lower() or "participant" in str(e).lower():
                            logger.info(f"[{phone}] Already a member")
                            return True
                        raise
                else:
                    # Public channel - use username/link
                    try:
                        await client(JoinChannelRequest(channel_url))
                        logger.success(f"[{phone}] Successfully joined public channel")
                    except Exception as e:
                        if "already" in str(e).lower() or "participant" in str(e).lower():
                            logger.info(f"[{phone}] Already a member")
                            return True
                        raise
                
                # Account-level delay
                await DelayManager.wait('join')
                
                return True
                
            except FloodWaitError as e:
                logger.warning(f"[{phone}] FloodWait: {e.seconds}s")
                await asyncio.sleep(e.seconds)
                return False
                
            except ChannelPrivateError:
                logger.error(f"[{phone}] Channel is private or you're banned")
                return False
                
            except InviteHashExpiredError:
                logger.error(f"[{phone}] Invite link has expired")
                return False
                
            except Exception as e:
                logger.error(f"[{phone}] Failed to join: {e}")
                return False
        
        # Run all accounts in parallel
        logger.info("Starting parallel execution for all accounts...")
        
        tasks = [
            join_for_account(phone, client)
            for phone, client in clients_dict.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate totals
        total_joined = 0
        total_failed = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Account {i+1} error: {result}")
                total_failed += 1
            elif result:
                total_joined += 1
            else:
                total_failed += 1
        
        print(f"\n{'='*70}")
        print(f"JOIN CHANNELS COMPLETED")
        print(f"{'='*70}")
        print(f"Successfully Joined: {total_joined}")
        print(f"Failed: {total_failed}")
        print(f"Accounts Used: {len(clients_dict)}")
        print(f"{'='*70}\n")
        
        status.show_success("Join operation completed")
        input("\nPress Enter to continue...")
        
    except Exception as e:
        logger.error(f"Join channels error: {e}")
        input("\nPress Enter to continue...")

