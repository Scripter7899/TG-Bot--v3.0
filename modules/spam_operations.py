"""
Spam Operations Module
Anti-spam and mass reporting features
"""

import asyncio
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.types import InputReportReasonSpam, InputReportReasonFake
from telethon.events import NewMessage
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator
import re

status = StatusIndicator()

async def mass_report():
    """Mass Report multiple users/groups"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        print("\nEnter targets to report (one per line, empty line to finish):")
        targets = []
        while True:
            target = input("> ").strip()
            if not target:
                break
            targets.append(target)
        
        if not targets:
            status.show_error("No targets provided")
            return
        
        print("\nReport Reason:")
        print("1. Spam")
        print("2. Fake Account")
        print("3. Violence")
        print("4. Other")
        reason_choice = input("Select reason (1-4): ").strip()
        
        from telethon.tl.types import InputReportReasonViolence, InputReportReasonOther
        reason_map = {
            '1': InputReportReasonSpam(),
            '2': InputReportReasonFake(),
            '3': InputReportReasonViolence(),
            '4': InputReportReasonOther()
        }
        reason = reason_map.get(reason_choice, InputReportReasonSpam())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        print(f"\n{'='*70}")
        print(f"MASS REPORTING {len(targets)} TARGETS")
        print(f"{'='*70}\n")
        
        success = 0
        failed = 0
        
        for idx, target in enumerate(targets, 1):
            try:
                entity = await client.get_entity(target)
                await client(ReportPeerRequest(peer=entity, reason=reason, message=""))
                print(f"[{idx}/{len(targets)}] ✅ Reported: {target}")
                success += 1
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"[{idx}/{len(targets)}] ❌ Failed: {target} - {str(e)}")
                failed += 1
        
        print(f"\n{'='*70}")
        print(f"Success: {success} | Failed: {failed}")
        print(f"{'='*70}\n")
        
        logger.success(f"Mass report complete: {success} reported")
        status.show_success(f"Reported {success}/{len(targets)} targets")
        
    except Exception as e:
        logger.error(f"Failed mass report: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def auto_report_spam():
    """Auto Report Spam messages in real-time"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username to monitor: ").strip()
        
        # Spam keywords
        print("\nEnter spam keywords (one per line, empty to finish):")
        spam_keywords = []
        while True:
            keyword = input("> ").strip().lower()
            if not keyword:
                break
            spam_keywords.append(keyword)
        
        if not spam_keywords:
            spam_keywords = ['buy now', 'click here', 'free money', 'earn $', 'limited offer']
            print(f"\nUsing default keywords: {spam_keywords}")
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        group_entity = await client.get_entity(group)
        
        print(f"\n{'='*70}")
        print(f"AUTO SPAM REPORTER ACTIVE")
        print(f"Monitoring: {group}")
        print(f"Keywords: {spam_keywords}")
        print(f"{'='*70}")
        print("Press Ctrl+C to stop\n")
        
        reported_count = 0
        
        @client.on(NewMessage(chats=group_entity))
        async def handler(event):
            nonlocal reported_count
            message_text = event.message.text.lower() if event.message.text else ""
            
            # Check for spam keywords
            for keyword in spam_keywords:
                if keyword in message_text:
                    try:
                        # Report message
                        from telethon.tl.functions.messages import ReportRequest
                        await client(ReportRequest(
                            peer=group_entity,
                            id=[event.message.id],
                            reason=InputReportReasonSpam(),
                            message=""
                        ))
                        reported_count += 1
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 Reported spam: '{message_text[:50]}...'")
                        logger.info(f"Auto-reported spam message: {event.message.id}")
                        break
                    except Exception as e:
                        logger.error(f"Failed to report: {e}")
        
        # Run until interrupted
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        print(f"\n\nStopped. Total spam messages reported: {reported_count}\n")
        status.show_success(f"Reported {reported_count} spam messages")
    except Exception as e:
        logger.error(f"Failed auto report: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def spam_filter():
    """Filter and identify spam patterns"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username to analyze: ").strip()
        limit = int(input("Analyze last N messages (default 100): ").strip() or "100")
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(group)
        
        status.show_processing("Analyzing messages for spam patterns...")
        
        # Spam patterns
        spam_patterns = [
            r'(buy|click|visit)\s+(now|here)',
            r'(free|earn)\s+(\$|money)',
            r'limited\s+(time|offer)',
            r'(http|https)://bit\.ly',
            r'(telegram|whatsapp)\s*:\s*\+?\d+',
            r'join\s+(channel|group)',
        ]
        
        spam_messages = []
        total_messages = 0
        
        async for message in client.iter_messages(entity, limit=limit):
            total_messages += 1
            if message.text:
                text_lower = message.text.lower()
                for pattern in spam_patterns:
                    if re.search(pattern, text_lower):
                        spam_messages.append({
                            'id': message.id,
                            'sender': message.sender_id,
                            'text': message.text[:100],
                            'date': message.date
                        })
                        break
        
        print(f"\n{'='*70}")
        print("SPAM FILTER ANALYSIS")
        print(f"{'='*70}")
        print(f"Total Messages Analyzed: {total_messages}")
        print(f"Spam Messages Detected: {len(spam_messages)}")
        print(f"Spam Rate: {(len(spam_messages) / total_messages * 100):.1f}%")
        print(f"{'='*70}\n")
        
        if spam_messages:
            print("Recent Spam Messages:")
            for idx, msg in enumerate(spam_messages[:10], 1):
                print(f"{idx}. [{msg['date']}] ID:{msg['id']}")
                print(f"   {msg['text']}")
                print(f"{'-'*70}")
        
        status.show_success(f"Found {len(spam_messages)} spam messages")
        
    except Exception as e:
        logger.error(f"Failed spam filter: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def block_spam_users():
    """Block users matching spam criteria"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username to scan: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(group)
        
        status.show_processing("Scanning for spam users...")
        
        # Criteria for spam users
        spam_users = []
        checked = 0
        
        async for message in client.iter_messages(entity, limit=200):
            if message.sender_id and message.text:
                checked += 1
                text_lower = message.text.lower()
                
                # Check spam indicators
                spam_score = 0
                if 'http' in text_lower or 'https' in text_lower:
                    spam_score += 1
                if any(word in text_lower for word in ['free', 'earn', 'money', 'click', 'buy']):
                    spam_score += 1
                if len(message.text) > 500:
                    spam_score += 1
                
                if spam_score >= 2:
                    if message.sender_id not in [u['id'] for u in spam_users]:
                        try:
                            sender = await client.get_entity(message.sender_id)
                            spam_users.append({
                                'id': message.sender_id,
                                'username': sender.username if hasattr(sender, 'username') else 'No username',
                                'name': f"{sender.first_name} {sender.last_name or ''}".strip()
                            })
                        except Exception:
                            pass
        
        if not spam_users:
            print("\nNo spam users detected\n")
            status.show_success("No spam users found")
            return
        
        print(f"\n{'='*70}")
        print(f"DETECTED {len(spam_users)} POTENTIAL SPAM USERS")
        print(f"{'='*70}\n")
        
        for idx, user in enumerate(spam_users, 1):
            print(f"{idx}. {user['name']} (@{user['username']})")
        
        confirm = input(f"\nBlock all {len(spam_users)} users? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled")
            return
        
        blocked = 0
        for user in spam_users:
            try:
                await client(BlockRequest(id=user['id']))
                blocked += 1
                print(f"✅ Blocked: {user['name']}")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ Failed to block {user['name']}: {e}")
        
        logger.success(f"Blocked {blocked} spam users")
        status.show_success(f"Blocked {blocked}/{len(spam_users)} users")
        
    except Exception as e:
        logger.error(f"Failed to block spam users: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def report_fake_accounts():
    """Report fake/impersonation accounts"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        print("\nEnter fake accounts to report (one per line, empty to finish):")
        fake_accounts = []
        while True:
            account = input("> ").strip()
            if not account:
                break
            fake_accounts.append(account)
        
        if not fake_accounts:
            status.show_error("No accounts provided")
            return
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        print(f"\n{'='*70}")
        print(f"REPORTING {len(fake_accounts)} FAKE ACCOUNTS")
        print(f"{'='*70}\n")
        
        success = 0
        for idx, account in enumerate(fake_accounts, 1):
            try:
                entity = await client.get_entity(account)
                await client(ReportPeerRequest(
                    peer=entity,
                    reason=InputReportReasonFake(),
                    message="Fake/impersonation account"
                ))
                print(f"[{idx}/{len(fake_accounts)}] ✅ Reported: {account}")
                success += 1
                await asyncio.sleep(2)
            except Exception as e:
                print(f"[{idx}/{len(fake_accounts)}] ❌ Failed: {account}")
                logger.error(f"Failed to report {account}: {e}")
        
        print(f"\n{'='*70}")
        print(f"Reported: {success}/{len(fake_accounts)}")
        print(f"{'='*70}\n")
        
        logger.success(f"Reported {success} fake accounts")
        status.show_success(f"Reported {success} accounts")
        
    except Exception as e:
        logger.error(f"Failed to report fake accounts: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def anti_spam_monitor():
    """Monitor groups for spam activity"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        print("\nEnter groups to monitor (one per line, empty to finish):")
        groups = []
        while True:
            group = input("> ").strip()
            if not group:
                break
            groups.append(group)
        
        if not groups:
            status.show_error("No groups provided")
            return
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        # Get group entities
        group_entities = []
        for group in groups:
            try:
                entity = await client.get_entity(group)
                group_entities.append(entity)
            except Exception as e:
                logger.error(f"Failed to get {group}: {e}")
        
        if not group_entities:
            status.show_error("No valid groups")
            return
        
        print(f"\n{'='*70}")
        print(f"ANTI-SPAM MONITOR ACTIVE")
        print(f"Monitoring {len(group_entities)} groups")
        print(f"{'='*70}")
        print("Press Ctrl+C to stop\n")
        
        spam_detected = 0
        
        @client.on(NewMessage(chats=group_entities))
        async def handler(event):
            nonlocal spam_detected
            
            if event.message.text:
                text_lower = event.message.text.lower()
                
                # Spam indicators
                spam_keywords = ['buy now', 'click here', 'free money', 'earn $', 'limited offer', 'join channel']
                
                for keyword in spam_keywords:
                    if keyword in text_lower:
                        spam_detected += 1
                        chat_title = event.chat.title if hasattr(event.chat, 'title') else 'Unknown'
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 SPAM in {chat_title}")
                        print(f"   Keyword: '{keyword}'")
                        print(f"   Message: {event.message.text[:80]}...")
                        print(f"{'-'*70}")
                        break
        
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        print(f"\n\nMonitoring stopped. Total spam detected: {spam_detected}\n")
        status.show_success(f"Detected {spam_detected} spam messages")
    except Exception as e:
        logger.error(f"Failed anti-spam monitor: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")
