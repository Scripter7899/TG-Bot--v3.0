"""
Enhanced Broadcast Module
Supports channel post replication with media
"""

import asyncio
import os
from pathlib import Path
from telethon.tl.types import InputMessagesFilterEmpty
from telethon import functions
import config
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import ProgressBar, StatusIndicator
from utils.file_parser import FileParser
from utils.delay_manager import DelayManager

status = StatusIndicator()

async def replicate_channel_post(source_url: str, target_chat, client):
    """
    Replicate a channel post with all media and formatting
    """
    try:
        # Parse URL
        post_info = FileParser.parse_channel_post_url(source_url)
        if not post_info:
            logger.error("Invalid channel post URL")
            return False
        
        # Get the message
        if post_info['is_private']:
            # Private channel (use channel ID)
            channel = await client.get_entity(int(f"-100{post_info['channel']}"))
        else:
            # Public channel
            channel = await client.get_entity(post_info['channel'])
        
        # Get single message by ID
        message = await client.get_messages(channel, ids=post_info['message_id'])
        
        if not message:
            logger.error("Message not found")
            return False
        
        # Send the message with media
        if message.media:
            # Has media - forward with media
            await client.send_file(
                target_chat,
                message.media,
                caption=message.text if message.text else None,
                formatting_entities=message.entities
            )
        else:
            # Text only
            await client.send_message(
                target_chat,
                message.text,
                formatting_entities=message.entities
            )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to replicate post: {e}")
        return False

async def broadcast_channel_post():
    """
    Feature 15 (Enhanced): Broadcast channel post to all targets
    """
    try:
        print(f"\n{'-'*70}")
        print("BROADCAST/MESSAGE SENDER [ALL ACCOUNTS]")
        print(f"{'-'*70}\n")
        
        # Get all accounts
        accounts = await db.get_all_accounts()
        if not accounts:
            status.show_error("No accounts found. Please login first.")
            return
        
        # Get channel post URL
        post_url = input("Enter Telegram channel post URL: ").strip()
        if not post_url:
            status.show_error("URL cannot be empty")
            return
        
        # Validate URL
        post_info = FileParser.parse_channel_post_url(post_url)
        if not post_info:
            status.show_error("Invalid channel post URL")
            return
        
        # Get target type
        print("\nTarget Options:")
        print("1. All Dialogs")
        print("2. All Groups")
        print("3. All Channels")
        print("4. Specific Chat")
        
        target_type = input("\nSelect target type (1-4): ").strip()
        
        specific_target = None
        if target_type == '4':
            specific_target = input("Enter chat username/link: ").strip()
        
        # Confirm
        print(f"\n{'-'*70}")
        print(f"Accounts: {len(accounts)}")
        print(f"Post URL: {post_url}")
        print(f"Target: {['All Dialogs', 'All Groups', 'All Channels', 'Specific Chat'][int(target_type)-1]}")
        print(f"Delay: 40-180 seconds per account")
        print(f"{'-'*70}\n")
        
        confirm = input("Start broadcast? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Broadcast cancelled")
            return
        
        # Start broadcasting
        total_sent = 0
        total_failed = 0
        
        progress = ProgressBar(len(accounts), "Broadcasting")
        
        async def broadcast_for_account(idx, account):
            nonlocal total_sent, total_failed
            phone = account[1]
            try:
                client = await session_manager.get_client(phone)
                if not client:
                    logger.warning(f"Skipping {phone} - not connected")
                    progress.update(idx)
                    return
                
                # status.show_processing(f"Broadcasting from {phone}") # Removed to prevent console spam in parallel
                
                # Get targets
                targets = []
                if target_type == '1':
                    dialogs = await client.get_dialogs()
                    targets = [d.entity for d in dialogs]
                elif target_type == '2':
                    dialogs = await client.get_dialogs()
                    targets = [d.entity for d in dialogs if d.is_group]
                elif target_type == '3':
                    dialogs = await client.get_dialogs()
                    targets = [d.entity for d in dialogs if d.is_channel]
                elif target_type == '4':
                    entity = await client.get_entity(specific_target)
                    targets = [entity]
                
                # Send to each target
                account_sent = 0
                account_failed = 0
                
                for target in targets:
                    try:
                        success = await replicate_channel_post(post_url, target, client)
                        if success:
                            account_sent += 1
                        else:
                            account_failed += 1
                        
                        # Small delay between targets (5-15 seconds)
                        await DelayManager.wait('react', custom_range=(5, 15))
                        
                    except Exception as e:
                        logger.error(f"Failed to send to target: {e}")
                        account_failed += 1
                
                logger.success(f"{phone}: Sent {account_sent}, Failed {account_failed}")
                
                # Update totals safely (in a real scenario use a lock, but here += is atomic enough for display)
                total_sent += account_sent
                total_failed += account_failed
                
                # Update progress
                progress.update(idx)
                
            except Exception as e:
                logger.error(f"Error with account {phone}: {e}")
                progress.update(idx)

        # Run all accounts in parallel
        logger.info("Starting parallel broadcast...")
        tasks = [broadcast_for_account(i+1, acc) for i, acc in enumerate(accounts)]
        await asyncio.gather(*tasks)
        
        # Final summary
        print(f"\n{'-'*70}")
        print("BROADCAST COMPLETE")
        print(f"{'-'*70}")
        print(f"Total Sent: {total_sent}")
        print(f"Total Failed: {total_failed}")
        print(f"Accounts Used: {len(accounts)}")
        print(f"{'-'*70}\n")
        
        status.show_success(f"Broadcast complete! Sent: {total_sent}, Failed: {total_failed}")
        
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
