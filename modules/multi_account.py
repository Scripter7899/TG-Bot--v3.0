"""
Multi-Account Operations Module for FULL-TG v3.0 - ENHANCED
Features 14-18: Mass operations with all accounts
ENHANCED: CSV support, bulk operations, smart delays
"""

import asyncio
import random
from pathlib import Path
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.errors import (
    FloodWaitError, UserPrivacyRestrictedError, UserNotMutualContactError,
    UserChannelsTooMuchError, ChatAdminRequiredError, PeerFloodError
)
import config
from core.session_manager import session_manager
from core.database import db
from core.rate_limiter import rate_limiter
from core.logger import logger, log_added_user, log_error_user
from ui.progress import ProgressBar, StatusIndicator, Counter
from utils.file_parser import FileParser
from utils.delay_manager import DelayManager

status = StatusIndicator()

async def mass_invite_all_accounts():
    """Feature 14 (ENHANCED): Group Members Adder [All Accounts] - PARALLEL EXECUTION"""
    try:
        print("\n" + "="*70)
        print("⭐ GROUP MEMBERS ADDER [ALL ACCOUNTS]")
        print("="*70 + "\n")
        
        # Choose source type
        print("Source Options:")
        print("1. Scrape from Group")
        print("2. Import from CSV File")
        
        source_choice = input("\nSelect source (1-2): ").strip()
        
        members_to_add = []
        target_group = input("Enter target group username/link: ").strip()
        
        # Get all clients
        clients_dict = await session_manager.get_all_clients()
        
        if not clients_dict:
            status.show_error("No active accounts found. Please login first.")
            return
        
        clients = list(clients_dict.values())
        phones = list(clients_dict.keys())
        
        print(f"\nUsing {len(clients)} account(s) for mass invite")
        
        if source_choice == '1':
            # Scrape from group
            source_group = input("Enter source group username/link: ").strip()
            limit = int(input("How many members to scrape? (0 for all): ").strip() or "0")
            
            status.show_processing(f"Scraping members from {source_group}")
            
            client = clients[0]  # Use first client to scrape
            try:
                source_entity = await client.get_entity(source_group)
                
                async for user in client.iter_participants(source_entity, limit=limit if limit > 0 else None):
                    if not user.bot and not user.deleted:
                        members_to_add.append(user)
                
                logger.info(f"Scraped {len(members_to_add)} members")
                
            except Exception as e:
                logger.error(f"Failed to scrape members: {e}")
                return
        
        elif source_choice == '2':
            # Import from CSV
            csv_file = input("Enter path to CSV file: ").strip()
            
            status.show_processing(f"Parsing CSV file: {csv_file}")
            
            usernames = FileParser.parse_usernames_csv(csv_file)
            
            if not usernames:
                status.show_error("No usernames found in CSV file")
                return
            
            logger.info(f"Parsed {len(usernames)} usernames from CSV")
            
            # Get user entities
            client = clients[0]
            status.show_processing("Fetching user entities...")
            
            for username in usernames:
                try:
                    user = await client.get_entity(username)
                    if not user.bot and not user.deleted:
                        members_to_add.append(user)
                except Exception as e:
                    logger.warning(f"Could not fetch user {username}: {e}")
            
            logger.info(f"Fetched {len(members_to_add)} valid users")
        
        if not members_to_add:
            status.show_error("No members to add")
            return
        
        # Get target entity
        try:
            target_entity = await clients[0].get_entity(target_group)
        except Exception as e:
            logger.error(f"Failed to get target group: {e}")
            return
        
        # Configurable Delays
        print("\nDelay Configuration:")
        min_delay_input = input("Min delay between invites (seconds, default 60): ").strip()
        max_delay_input = input("Max delay between invites (seconds, default 180): ").strip()
        
        try:
            min_delay = int(min_delay_input) if min_delay_input else 60
            max_delay = int(max_delay_input) if max_delay_input else 180
            
            if min_delay < 1:
                print("⚠️  Warning: Min delay too low, using 1 second")
                min_delay = 1
            if max_delay < min_delay:
                print("⚠️  Warning: Max delay < min delay, using min + 30")
                max_delay = min_delay + 30
        except ValueError:
            print("⚠️  Invalid input, using defaults (60-180s)")
            min_delay = 60
            max_delay = 180
        
        # Confirm
        print(f"\n{'-'*70}")
        print(f"Members to Add: {len(members_to_add)}")
        print(f"Target Group: {target_group}")
        print(f"Accounts: {len(clients)}")
        print(f"Mode: PARALLEL (all accounts work simultaneously)")
        print(f"Delay: {min_delay}-{max_delay} seconds per invite per account")
        print(f"{'-'*70}\n")
        
        confirm = input("Start adding members? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        # Parallel execution - divide members among accounts
        members_per_account = len(members_to_add) // len(clients)
        
        async def add_for_account(phone, client, members_chunk, account_index):
            """Add members for a single account with account-level delays"""
            added = 0
            errors = 0
            
            total_members = len(members_chunk)
            logger.info(f"[{phone}] Starting to add {total_members} members")
            
            for idx, user in enumerate(members_chunk, 1):
                try:
                    # Reconnect if needed
                    if not client.is_connected():
                        await client.connect()
                    
                    # Rate limiting
                    await rate_limiter.wait_if_needed(phone, 'invite')
                    
                    # Configurable delay
                    delay = random.randint(min_delay, max_delay)
                    await asyncio.sleep(delay)
                    
                    # Add user
                    await client(InviteToChannelRequest(
                        target_entity,
                        [user]
                    ))
                    
                    added += 1
                    log_added_user(user.username or str(user.id), user.id, target_group)
                    logger.success(f"[{phone}] Added @{user.username or user.id}")
                    
                except FloodWaitError as e:
                    rate_limiter.set_flood_wait(phone, 'invite', e.seconds)
                    logger.warning(f"[{phone}] FloodWait: {e.seconds}s")
                    errors += 1
                    await asyncio.sleep(e.seconds)
                    
                except (UserPrivacyRestrictedError, UserNotMutualContactError, 
                        UserChannelsTooMuchError) as e:
                    errors += 1
                    log_error_user(user.username or str(user.id), user.id, target_group, str(e))
                    
                except PeerFloodError:
                    logger.error(f"[{phone}] Peer flood - stopping this account")
                    break
                    
                except Exception as e:
                    errors += 1
                    log_error_user(user.username or str(user.id), user.id, target_group, str(e))
                
                # Progress status after each attempt
                logger.info(f"[{phone}] Progress: {idx}/{total_members} | ✓ {added} | ✗ {errors}")
                
                # Account-level delay (60-180 seconds)
                if idx < total_members:  # Don't delay after last member
                    delay = random.randint(60, 180)
                    logger.info(f"[{phone}] Next invite in {delay} seconds...")
                    await asyncio.sleep(delay)
            
            logger.success(f"[{phone}] Complete: Added {added}, Errors {errors}")
            return added, errors
        
        # Divide members among accounts
        tasks = []
        for i, (phone, client) in enumerate(clients_dict.items()):
            start_idx = i * members_per_account
            end_idx = start_idx + members_per_account if i < len(clients) - 1 else len(members_to_add)
            members_chunk = members_to_add[start_idx:end_idx]
            
            tasks.append(add_for_account(phone, client, members_chunk, i))
        
        # Run all accounts in parallel
        logger.info("Starting parallel execution for all accounts...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate totals
        total_added = 0
        total_errors = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Account {i+1} error: {result}")
            else:
                added, errors = result
                total_added += added
                total_errors += errors
        
        print(f"\n{'='*70}")
        print(f"MASS INVITE COMPLETED")
        print(f"{'='*70}")
        print(f"Total Members: {len(members_to_add)}")
        print(f"Successfully Added: {total_added}")
        print(f"Errors: {total_errors}")
        print(f"Accounts Used: {len(clients)}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Mass invite error: {e}")

async def join_groups_all_accounts():
    """Feature 16 (ENHANCED): Join groups with all accounts - PARALLEL EXECUTION"""
    try:
        print("\n" + "="*70)
        print("⭐ JOIN GROUPS [ALL ACCOUNTS]")
        print("="*70 + "\n")
        
        print("Input Options:")
        print("1. Enter groups manually")
        print("2. Import from text file")
        
        input_choice = input("\nSelect option (1-2): ").strip()
        
        groups = []
        
        if input_choice == '1':
            # Manual entry
            print("\nEnter group links (one per line, empty line to finish):")
            while True:
                group = input().strip()
                if not group:
                    break
                groups.append(group)
        
        elif input_choice == '2':
            # Import from file
            file_path = input("Enter path to text file: ").strip()
            groups = FileParser.parse_groups_file(file_path)
        
        if not groups:
            status.show_error("No groups provided")
            return
        
        # Get all clients
        clients_dict = await session_manager.get_all_clients()
        
        if not clients_dict:
            status.show_error("No active accounts found")
            return
        
        print(f"\n{'-'*70}")
        print(f"Groups to Join: {len(groups)}")
        print(f"Accounts: {len(clients_dict)}")
        print(f"Mode: PARALLEL (all accounts work simultaneously)")
        print(f"Delay: 60-240 seconds per group per account")
        print(f"Note: Each account operates independently")
        print(f"{'-'*70}\n")
        
        confirm = input("Start joining? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        # Parallel execution - each account runs independently
        async def join_for_account(phone, client):
            """Join groups for a single account with account-level delays"""
            account_joined = 0
            account_failed = 0
            
            total_groups = len(groups)
            logger.info(f"[{phone}] Starting to join {total_groups} groups")
            
            for idx, group in enumerate(groups, 1):
                try:
                    # Reconnect if needed
                    if not client.is_connected():
                        await client.connect()
                    
                    # Check if it's an invite link
                    invite_hash = None
                    if 't.me/+' in group or 't.me/joinchat/' in group:
                        # Extract invite hash
                        import re
                        patterns = [
                            r't\.me/\+([A-Za-z0-9_-]+)',
                            r't\.me/joinchat/([A-Za-z0-9_-]+)',
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, group)
                            if match:
                                invite_hash = match.group(1)
                                break
                    
                    # Join based on type
                    if invite_hash:
                        # Private group/channel - use invite hash
                        from telethon.tl.functions.messages import ImportChatInviteRequest
                        await client(ImportChatInviteRequest(invite_hash))
                        logger.success(f"[{phone}] Joined {group} via invite link")
                    else:
                        # Public group/channel
                        await client(JoinChannelRequest(group))
                        logger.success(f"[{phone}] Joined {group}")
                    
                    account_joined += 1
                    
                except FloodWaitError as e:
                    logger.warning(f"[{phone}] FloodWait: {e.seconds}s for {group}")
                    account_failed += 1
                    await asyncio.sleep(e.seconds)
                    
                except Exception as e:
                    logger.error(f"[{phone}] Failed to join {group}: {e}")
                    account_failed += 1
                
                # Progress status after each attempt
                logger.info(f"[{phone}] Progress: {idx}/{total_groups} | ✓ {account_joined} | ✗ {account_failed}")
                
                # Account-level delay (60-240 seconds per group)
                if idx < total_groups:  # Don't delay after last group
                    delay = random.randint(60, 240)
                    logger.info(f"[{phone}] Next join in {delay} seconds...")
                    await asyncio.sleep(delay)
            
            logger.success(f"[{phone}] Complete: Joined {account_joined}, Failed {account_failed}")
            return account_joined, account_failed
        
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
            else:
                joined, failed = result
                total_joined += joined
                total_failed += failed
        
        print(f"\n{'='*70}")
        print(f"JOIN GROUPS COMPLETED")
        print(f"{'='*70}")
        print(f"Total Joined: {total_joined}")
        print(f"Total Failed: {total_failed}")
        print(f"Accounts Used: {len(clients_dict)}")
        print(f"{'='*70}\n")
        
        status.show_success("Join operation completed")
        
    except Exception as e:
        logger.error(f"Join groups error: {e}")

async def leave_groups_all_accounts():
    """Feature 17: Leave groups with all accounts"""
    try:
        print("\n" + "="*70)
        print("LEAVE GROUPS [ALL ACCOUNTS]")
        print("="*70 + "\n")
        
        print("Options:")
        print("1. Leave all groups")
        print("2. Leave specific groups")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        # Get all clients
        clients_dict = await session_manager.get_all_clients()
        
        if not clients_dict:
            status.show_error("No active accounts found")
            return
        
        for phone, client in clients_dict.items():
            try:
                logger.info(f"Processing {phone}")
                
                dialogs = await client.get_dialogs()
                groups = [d for d in dialogs if d.is_group or d.is_channel]
                
                if choice == '2':
                    print(f"\nGroups for {phone}:")
                    for i, g in enumerate(groups, 1):
                        print(f"{i}. {g.name}")
                    
                    indices = input("Enter group numbers to leave (comma-separated): ").strip()
                    indices = [int(i.strip())-1 for i in indices.split(',')]
                    groups = [groups[i] for i in indices if 0 <= i < len(groups)]
                
                # Leave groups
                for group in groups:
                    try:
                        await client(LeaveChannelRequest(group.entity))
                        logger.success(f"{phone} left {group.name}")
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.error(f"Failed to leave {group.name}: {e}")
                
            except Exception as e:
                logger.error(f"Error for {phone}: {e}")
        
        status.show_success("Leave operation completed")
        
    except Exception as e:
        logger.error(f"Leave groups error: {e}")

async def show_all_active_accounts():
    """Feature 18: Show all active accounts"""
    try:
        accounts = await db.get_all_accounts()
        clients_dict = await session_manager.get_all_clients()
        
        print(f"\n{'='*70}")
        print(f"⭐ ACTIVE ACCOUNTS ({len(accounts)})")
        print(f"{'='*70}\n")
        
        for i, account in enumerate(accounts, 1):
            phone = account[1]
            status_text = account[6]
            last_used = account[7]
            
            # Check if currently connected
            connected = "🟢 Connected" if phone in clients_dict else "⚪ Disconnected"
            
            print(f"{i}. {phone}")
            print(f"   Status: {status_text}")
            print(f"   Connection: {connected}")
            print(f"   Last Used: {last_used or 'Never'}")
            print()
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Error showing accounts: {e}")
