"""
Auto-Posting Module
Scheduled posting to multiple groups
"""

import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
from telethon import functions
from telethon.errors import FloodWaitError
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator
import hashlib
from utils.delay_manager import DelayManager
from utils.file_parser import FileParser
from modules.enhanced_broadcast import replicate_channel_post

status = StatusIndicator()

async def auto_post_to_groups():
    """
    Feature 96 (MAXIMIZED): Auto-post to groups with scheduling
    Mode 1: Post now (1 cycle + exit)
    Mode 2: Post at specific time (wait + 1 cycle + exit)
    Mode 3: Recurring (infinite cycles in background)
    """
    try:
        print(f"\n{'-'*70}")
        print("⭐ AUTO-POST TO GROUPS [ALL ACCOUNTS]")
        print(f"{'-'*70}\n")
        
        # Get content type
        print("Content Options:")
        print("1. Text message")
        print("2. Channel post URL (replicate)")
        print("3. Media file (photo/video/document)")
        
        content_choice = input("\nSelect content type (1-3): ").strip()
        
        content_text = None
        content_file = None
        channel_url = None
        
        if content_choice == '1':
            content_text = input("Enter message text: ").strip()
        elif content_choice == '2':
            channel_url = input("Enter channel post URL: ").strip()
        elif content_choice == '3':
            content_file = input("Enter path to media file: ").strip()
            
            # QUICK WIN 1: Media File Validation
            if not Path(content_file).exists():
                print(f"\n❌ Error: Media file not found: {content_file}")
                print("Please check the file path and try again.")
                input("\nPress Enter to continue...")
                return
            
            file_size = Path(content_file).stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size > 2_000_000_000:  # 2GB Telegram limit
                print(f"\n❌ Error: File too large ({file_size_mb:.1f} MB)")
                print("Telegram limit: 2000 MB (2 GB)")
                print("Please use a smaller file.")
                input("\nPress Enter to continue...")
                return
            
            print(f"✓ Media file validated ({file_size_mb:.1f} MB)")
            content_text = input("Enter caption (optional): ").strip()
        
        # Get target groups
        print("\nTarget Groups:")
        print("1. All groups")
        print("2. Specific groups (from file)")
        print("3. Enter manually")
        
        target_choice = input("\nSelect option (1-3): ").strip()
        
        target_groups = []
        
        if target_choice == '2':
            file_path = input("Enter path to groups file: ").strip()
            target_groups = FileParser.parse_groups_file(file_path)
        elif target_choice == '3':
            print("Enter group usernames (one per line, empty to finish):")
            while True:
                group = input().strip()
                if not group:
                    break
                target_groups.append(group)
        
        # Get schedule
        print("\nSchedule Options:")
        print("1. Post now (1 cycle + exit)")
        print("2. Post once at specific time (wait + 1 cycle + exit)")
        print("3. Recurring (infinite cycles in background)")
        
        schedule_choice = input("\nSelect option (1-3): ").strip()
        
        scheduled_time = None
        recurring_interval = None
        
        if schedule_choice == '2':
            # Get scheduled time
            print("\nEnter scheduled time:")
            date_str = input("Date (YYYY-MM-DD): ").strip()
            time_str = input("Time (HH:MM): ").strip()
            try:
                scheduled_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                if scheduled_time <= datetime.now():
                    print("Error: Scheduled time must be in the future")
                    return
            except ValueError:
                print("Error: Invalid date/time format")
                return
        
        elif schedule_choice == '3':
            # Get recurring interval
            print("\nRecurring Interval:")
            print("1. Hourly")
            print("2. Daily")
            interval_choice = input("Select interval (1-2): ").strip()
            recurring_interval = 'hourly' if interval_choice == '1' else 'daily'
        
        # Get accounts
        clients_dict = await session_manager.get_all_clients()
        
        if not clients_dict:
            status.show_error("No active accounts found")
            return
        
        # Confirm
        print(f"\n{'-'*70}")
        print(f"Content: {['Text', 'Channel Post', 'Media'][int(content_choice)-1]}")
        print(f"Targets: {len(target_groups) if target_groups else 'All groups'}")
        print(f"Accounts: {len(clients_dict)}")
        
        if schedule_choice == '1':
            print(f"Schedule: Post now (1 cycle)")
        elif schedule_choice == '2':
            print(f"Schedule: Post at {scheduled_time.strftime('%Y-%m-%d %H:%M')} (1 cycle)")
        else:
            print(f"Schedule: Recurring {recurring_interval} (infinite cycles)")
            print(f"⚠️  WARNING: This will run in background until manually stopped!")
        
        # QUICK WIN 2: Configurable Delays
        print("\nDelay Configuration:")
        min_delay_input = input("Min delay between groups (seconds, default 120): ").strip()
        max_delay_input = input("Max delay between groups (seconds, default 300): ").strip()
        
        try:
            min_delay = int(min_delay_input) if min_delay_input else 120
            max_delay = int(max_delay_input) if max_delay_input else 300
            
            if min_delay < 10:
                print("⚠️  Warning: Min delay too low, using 10 seconds")
                min_delay = 10
            if max_delay < min_delay:
                print("⚠️  Warning: Max delay < min delay, using min + 60")
                max_delay = min_delay + 60
        except ValueError:
            print("⚠️  Invalid input, using defaults (120-300s)")
            min_delay = 120
            max_delay = 300
        
        print(f"Delay: {min_delay}-{max_delay} seconds between groups")
        print(f"{'-'*70}\n")
        
        confirm = input("Start posting? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        # Execute based on schedule choice
        if schedule_choice == '1':
            # Mode 1: Post now
            await execute_post_cycle(clients_dict, content_choice, content_text, content_file, 
                                    channel_url, target_choice, target_groups, min_delay, max_delay)
            input("\nPress Enter to continue...")
        
        elif schedule_choice == '2':
            # Mode 2: Wait then post once
            wait_seconds = (scheduled_time - datetime.now()).total_seconds()
            print(f"\nWaiting until {scheduled_time.strftime('%Y-%m-%d %H:%M')}...")
            print(f"({int(wait_seconds)} seconds)")
            await asyncio.sleep(wait_seconds)
            
            await execute_post_cycle(clients_dict, content_choice, content_text, content_file,
                                    channel_url, target_choice, target_groups, min_delay, max_delay)
            input("\nPress Enter to continue...")
        
        else:
            # Mode 3: Recurring in background
            from core.background_tasks import background_tasks
            
            async def recurring_post_task():
                """Background task for recurring posts"""
                cycle_num = 1
                while not background_tasks.should_stop('auto_post_recurring'):
                    try:
                        logger.info(f"Starting auto-post cycle #{cycle_num}")
                        
                        await execute_post_cycle(clients_dict, content_choice, content_text, 
                                               content_file, channel_url, target_choice, target_groups, min_delay, max_delay)
                        
                        logger.success(f"Completed auto-post cycle #{cycle_num}")
                        
                        # Wait for next cycle
                        if recurring_interval == 'hourly':
                            wait_time = 3600  # 1 hour
                            logger.info(f"Next cycle in 1 hour...")
                        else:
                            wait_time = 86400  # 24 hours
                            logger.info(f"Next cycle in 24 hours...")
                        
                        # Sleep in chunks to allow stopping
                        for _ in range(wait_time):
                            if background_tasks.should_stop('auto_post_recurring'):
                                break
                            await asyncio.sleep(1)
                        
                        cycle_num += 1
                    
                    except Exception as e:
                        logger.error(f"Error in recurring post cycle: {e}")
                        await asyncio.sleep(60)  # Wait 1 minute before retry
            
            # Start background task
            if background_tasks.start_task('auto_post_recurring', recurring_post_task()):
                print(f"\n✅ Recurring auto-post started in background!")
                print(f"   Interval: {recurring_interval}")
                print(f"   To stop: Use option 121 (Automated Workflows) -> Stop Tasks")
                input("\nPress Enter to return to menu...")
            else:
                print("\n❌ Failed to start recurring task (already running?)")
                input("\nPress Enter to continue...")
        
    except Exception as e:
        logger.error(f"Auto-post error: {e}")
        input("\nPress Enter to continue...")

async def execute_post_cycle(clients_dict, content_choice, content_text, content_file,
                             channel_url, target_choice, target_groups, min_delay=120, max_delay=300):
    """Execute one complete posting cycle with configurable delays"""
    
    # Post function
    async def post_to_group(client, phone, group, content_type, content):
        """Post content to a single group"""
        try:
            # Get group name for logging
            group_name = group.title if hasattr(group, 'title') else str(group)
            group_id = str(group.id) if hasattr(group, 'id') else str(hash(group_name))
            
            post_successful = False
            content_for_hash = ""
            
            if content_type == '1':
                # Text message
                await client.send_message(group, content['text'])
                post_successful = True
                content_for_hash = content['text']
                
            elif content_type == '2':
                # Channel post replication
                success = await replicate_channel_post(content['url'], group, client)
                if success:
                    post_successful = True
                    content_for_hash = content['url']
                else:
                    logger.error(f"{phone} failed to post to {group_name}")
                    return False
                
            elif content_type == '3':
                # Media file
                await client.send_file(group, content['file'], caption=content.get('caption', ''))
                post_successful = True  # FIX: Added missing flag
                content_for_hash = content['file'] + content.get('caption', '')
                logger.success(f"{phone} posted to {group_name}")
            
            # P0: Track post history (FIX: Complete integration)
            if post_successful:
                content_hash = hashlib.md5(content_for_hash.encode()).hexdigest()
                
                try:
                    await db.add_post_history(
                        account_phone=phone,
                        group_id=group_id,
                        group_name=group_name,
                        content_type=content_type,
                        content_hash=content_hash,
                        status='success'
                    )
                    logger.info(f"[TRACKED] Post to {group_name} logged in history")
                except Exception as track_error:
                    logger.warning(f"Failed to track post history: {track_error}")
            
            return True
            
        except Exception as e:
            group_name = group.title if hasattr(group, 'title') else str(group)
            
            # QUICK WIN 3: Better Error Messages
            error_str = str(e)
            if "PEER_FLOOD" in error_str or "FLOOD_WAIT" in error_str:
                logger.error(f"{phone} RATE LIMITED in {group_name} - Slow down!")
            elif "CHAT_WRITE_FORBIDDEN" in error_str:
                logger.error(f"{phone} NO PERMISSION to post in {group_name}")
            elif "USER_BANNED" in error_str:
                logger.error(f"{phone} BANNED from {group_name}")
            elif "CHAT_ADMIN_REQUIRED" in error_str:
                logger.error(f"{phone} ADMIN REQUIRED in {group_name}")
            elif "SLOWMODE_WAIT" in error_str:
                logger.error(f"{phone} SLOWMODE active in {group_name}")
            else:
                logger.error(f"{phone} failed to post to {group_name}: {e}")
            
            return False
    
    # Post for single account
    async def post_for_account(phone, client):
        """Post to groups for a single account"""
        account_posted = 0
        account_failed = 0
        
        try:
            # Get target groups for this account
            if target_choice == '1':
                dialogs = await client.get_dialogs()
                # Filter to ONLY groups (megagroups), exclude channels
                groups = [d.entity for d in dialogs if d.is_group and hasattr(d.entity, 'megagroup') and d.entity.megagroup]
            else:
                groups = target_groups
            
            total_groups = len(groups)
            logger.info(f"[{phone}] Starting to post to {total_groups} groups")
            
            for idx, group in enumerate(groups, 1):
                # Prepare content
                content = {}
                if content_choice == '1':
                    content = {'text': content_text}
                elif content_choice == '2':
                    content = {'url': channel_url}
                elif content_choice == '3':
                    content = {'file': content_file, 'caption': content_text}
                
                # Post
                success = await post_to_group(client, phone, group, content_choice, content)
                
                if success:
                    account_posted += 1
                else:
                    account_failed += 1
                
                # Progress status
                logger.info(f"[{phone}] Progress: {idx}/{total_groups} | ✓ {account_posted} | ✗ {account_failed}")
                
                # Account-level delay between groups (configurable)
                if idx < total_groups:  # Don't delay after last group
                    delay = random.randint(min_delay, max_delay)
                    logger.info(f"[{phone}] Next message in {delay} seconds...")
                    await asyncio.sleep(delay)
            
            logger.success(f"[{phone}] Complete: Posted {account_posted}, Failed {account_failed}")
            return account_posted, account_failed
            
        except Exception as e:
            logger.error(f"[{phone}] Error: {e}")
            return account_posted, account_failed
    
    # Run all accounts in parallel
    logger.info("Starting parallel execution for all accounts...")
    
    tasks = [
        post_for_account(phone, client)
        for phone, client in clients_dict.items()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Calculate totals
    total_posted = 0
    total_failed = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Account {i+1} error: {result}")
        else:
            posted, failed = result
            total_posted += posted
            total_failed += failed
    
    print(f"\n{'-'*70}")
    print(f"AUTO-POST CYCLE COMPLETED")
    print(f"{'-'*70}")
    print(f"Total Posted: {total_posted}")
    print(f"Total Failed: {total_failed}")
    print(f"{'-'*70}\n")
    
    status.show_success(f"Posted {total_posted} times")

