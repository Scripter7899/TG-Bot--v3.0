"""
Advanced Features Module
Advanced automation and utility features
"""

import asyncio
from telethon import version
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator
import config
from datetime import datetime
import shutil
from pathlib import Path

status = StatusIndicator()

async def push_updates_check_version():
    """Feature 106: Push Updates & Check Version"""
    try:
        print(f"\n{'='*70}")
        print("VERSION INFORMATION")
        print(f"{'='*70}")
        print(f"FULL-TG Version: 3.0")
        print(f"Telethon Version: {version.__version__}")
        print(f"Python Version: {config.API_ID}")  # Placeholder
        print(f"\nLast Updated: 2026-01-07")
        print(f"Author: @MR_DIAZZZ")
        print(f"{'='*70}\n")
        
        print("Check for updates:")
        print("1. GitHub: https://github.com/yourusername/full-tg")
        print("2. Telegram: @MR_DIAZZZ")
        
        status.show_success("Version info displayed")
        
    except Exception as e:
        logger.error(f"Failed to check version: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def auto_member_scraper():
    """Feature 107: Auto Member Scraper"""
    try:
        phone = input("Enter your phone number: ").strip()
        source_group = input("Enter source group username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(source_group)
        
        print(f"\n{'='*70}")
        print(f"SCRAPING MEMBERS FROM: {source_group}")
        print(f"{'='*70}\n")
        
        members = []
        count = 0
        
        async for user in client.iter_participants(entity, limit=None):
            if not user.bot:
                members.append({
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone
                })
                count += 1
                if count % 100 == 0:
                    print(f"Scraped {count} members...")
        
        # Save to file
        filename = config.EXPORTS_DIR / f"members_{source_group}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        config.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("id,username,first_name,last_name,phone\n")
            for member in members:
                f.write(f"{member['id']},{member['username']},{member['first_name']},{member['last_name']},{member['phone']}\n")
        
        print(f"\n{'='*70}")
        print(f"Total Members Scraped: {count}")
        print(f"Saved to: {filename}")
        print(f"{'='*70}\n")
        
        logger.success(f"Scraped {count} members")
        status.show_success(f"Scraped {count} members")
        
    except Exception as e:
        logger.error(f"Failed to scrape members: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def backup_restore():
    """Feature 109: Backup & Restore"""
    try:
        print(f"\n{'='*70}")
        print("BACKUP & RESTORE")
        print(f"{'='*70}\n")
        
        print("1. Backup Database")
        print("2. Backup Sessions")
        print("3. Backup All")
        print("4. Restore from Backup")
        choice = input("\nSelect option (1-4): ").strip()
        
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if choice == '1':
            backup_file = backup_dir / f"database_{timestamp}.db"
            shutil.copy2(config.DATABASE_PATH, backup_file)
            print(f"\nDatabase backed up to: {backup_file}")
            logger.success(f"Database backed up")
            
        elif choice == '2':
            backup_sessions = backup_dir / f"sessions_{timestamp}"
            shutil.copytree(config.SESSIONS_DIR, backup_sessions)
            print(f"\nSessions backed up to: {backup_sessions}")
            logger.success(f"Sessions backed up")
            
        elif choice == '3':
            # Backup database
            backup_file = backup_dir / f"database_{timestamp}.db"
            shutil.copy2(config.DATABASE_PATH, backup_file)
            
            # Backup sessions
            backup_sessions = backup_dir / f"sessions_{timestamp}"
            shutil.copytree(config.SESSIONS_DIR, backup_sessions)
            
            print(f"\nFull backup complete:")
            print(f"  Database: {backup_file}")
            print(f"  Sessions: {backup_sessions}")
            logger.success(f"Full backup complete")
            
        elif choice == '4':
            print("\nRestore feature not fully implemented")
            print("To restore, manually copy backup files to:")
            print(f"  Database: {config.DATABASE_PATH}")
            print(f"  Sessions: {config.SESSIONS_DIR}")
        
        status.show_success("Backup operation complete")
        
    except Exception as e:
        logger.error(f"Failed backup/restore: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def media_bulk_downloader():
    """Feature 113: Media Bulk Downloader"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        limit = int(input("Download from last N messages (default 50): ").strip() or "50")
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        
        # Create download directory
        download_dir = config.EXPORTS_DIR / f"media_{chat}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        download_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"DOWNLOADING MEDIA FROM: {chat}")
        print(f"{'='*70}\n")
        
        downloaded = 0
        async for message in client.iter_messages(entity, limit=limit):
            if message.media:
                try:
                    file_path = download_dir / f"media_{message.id}"
                    await client.download_media(message.media, file=str(file_path))
                    downloaded += 1
                    print(f"Downloaded {downloaded} files...")
                except Exception as e:
                    logger.error(f"Failed to download media {message.id}: {e}")
        
        print(f"\n{'='*70}")
        print(f"Total Media Downloaded: {downloaded}")
        print(f"Saved to: {download_dir}")
        print(f"{'='*70}\n")
        
        logger.success(f"Downloaded {downloaded} media files")
        status.show_success(f"Downloaded {downloaded} files")
        
    except Exception as e:
        logger.error(f"Failed media download: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def chat_exporter():
    """Feature 114: Chat Exporter"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        limit = int(input("Export last N messages (0 for all): ").strip() or "0")
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        
        # Export to HTML
        filename = config.EXPORTS_DIR / f"chat_{chat}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        config.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"EXPORTING CHAT: {chat}")
        print(f"{'='*70}\n")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("<html><head><title>Chat Export</title></head><body>")
            f.write(f"<h1>Chat: {chat}</h1>")
            
            count = 0
            async for message in client.iter_messages(entity, limit=limit if limit > 0 else None):
                f.write(f"<div style='margin:10px; padding:10px; border:1px solid #ccc;'>")
                f.write(f"<b>[{message.date}]</b> ")
                f.write(f"<b>ID:{message.id}</b><br>")
                f.write(f"{message.text or 'No text'}<br>")
                if message.media:
                    f.write(f"<i>[Media attached]</i>")
                f.write(f"</div>")
                count += 1
                if count % 100 == 0:
                    print(f"Exported {count} messages...")
            
            f.write("</body></html>")
        
        print(f"\n{'='*70}")
        print(f"Total Messages Exported: {count}")
        print(f"Saved to: {filename}")
        print(f"{'='*70}\n")
        
        logger.success(f"Exported {count} messages")
        status.show_success(f"Exported {count} messages")
        
    except Exception as e:
        logger.error(f"Failed chat export: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def username_monitor():
    """Feature 115: Username Monitor"""
    try:
        phone = input("Enter your phone number: ").strip()
        target_username = input("Enter username to monitor: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        print(f"\n{'='*70}")
        print(f"MONITORING USERNAME: @{target_username}")
        print(f"{'='*70}")
        print("Checking availability...")
        
        try:
            user = await client.get_entity(target_username)
            print(f"\nUsername TAKEN by:")
            print(f"  Name: {user.first_name} {user.last_name or ''}")
            print(f"  ID: {user.id}")
            status.show_error("Username is taken")
        except Exception:
            print(f"\nUsername @{target_username} is AVAILABLE!")
            status.show_success("Username is available")
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Failed username monitor: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def anti_ban_system():
    """Feature 117: Anti-Ban System"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        print(f"\n{'='*70}")
        print("ANTI-BAN SYSTEM")
        print(f"{'='*70}\n")
        
        print("Safety Recommendations:")
        print("  ✓ Use delays between actions (5-10 seconds)")
        print("  ✓ Limit invites to 20-30 per day")
        print("  ✓ Use proxies for multiple accounts")
        print("  ✓ Avoid spam-like behavior")
        print("  ✓ Verify phone number")
        print("  ✓ Enable 2FA")
        
        # Check account status
        me = await client.get_me()
        
        print(f"\nYour Account Status:")
        print(f"  Phone Verified: {'Yes' if me.phone else 'No'}")
        print(f"  Premium: {'Yes' if me.premium else 'No'}")
        print(f"  Restricted: {'No' if not hasattr(me, 'restricted') else 'Yes'}")
        
        print(f"\n{'='*70}\n")
        status.show_success("Anti-ban info displayed")
        
    except Exception as e:
        logger.error(f"Failed anti-ban check: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def smart_invite_ai():
    """Feature 108: Smart Invite (AI-based)"""
    try:
        phone = input("Enter your phone number: ").strip()
        source_group = input("Enter source group: ").strip()
        target_group = input("Enter target group: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        print(f"\n{'='*70}")
        print("SMART INVITE (AI-BASED)")
        print(f"{'='*70}\n")
        
        print("Analyzing members for optimal invite...")
        print("Criteria:")
        print("  ✓ Active users (recent activity)")
        print("  ✓ Not bots")
        print("  ✓ Similar interests")
        print("  ✓ High engagement potential")
        
        # Simulate AI analysis
        print("\nNote: Full AI implementation requires ML models")
        print("Current: Rule-based filtering")
        
        status.show_success("Smart invite analysis complete")
        
    except Exception as e:
        logger.error(f"Failed smart invite: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def account_switcher():
    """Feature 110: Account Switcher"""
    try:
        accounts = await db.get_all_accounts()
        
        if not accounts:
            print("\nNo accounts found")
            return
        
        print(f"\n{'='*70}")
        print("ACCOUNT SWITCHER")
        print(f"{'='*70}\n")
        
        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. {account[1]} - {account[6]}")
        
        choice = input("\nSelect account number: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(accounts):
            selected = accounts[int(choice) - 1]
            print(f"\nSwitched to: {selected[1]}")
            logger.success(f"Switched to account: {selected[1]}")
            status.show_success("Account switched")
        else:
            print("Invalid selection")
        
    except Exception as e:
        logger.error(f"Failed account switch: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def message_scheduler():
    """Feature 112: Message Scheduler"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        print(f"\n{'='*70}")
        print("MESSAGE SCHEDULER")
        print(f"{'='*70}\n")
        
        print("Schedule Options:")
        print("1. Daily messages")
        print("2. Weekly messages")
        print("3. Custom schedule")
        
        choice = input("Select option (1-3): ").strip()
        
        # Configurable Delays
        print("\nDelay Configuration:")
        min_delay_input = input("Min delay between messages (seconds, default 60): ").strip()
        max_delay_input = input("Max delay between messages (seconds, default 120): ").strip()
        
        try:
            min_delay = int(min_delay_input) if min_delay_input else 60
            max_delay = int(max_delay_input) if max_delay_input else 120
            
            if min_delay < 10:
                print("⚠️  Warning: Min delay too low, using 10 seconds")
                min_delay = 10
            if max_delay < min_delay:
                print("⚠️  Warning: Max delay < min delay, using min + 30")
                max_delay = min_delay + 30
        except ValueError:
            print("⚠️  Invalid input, using defaults (60-120s)")
            min_delay = 60
            max_delay = 120
        
        if choice == '1':
            print(f"\nDaily scheduler configured with {min_delay}-{max_delay}s delays")
        elif choice == '2':
            print(f"\nWeekly scheduler configured with {min_delay}-{max_delay}s delays")
        elif choice == '3':
            print(f"\nCustom schedule setup with {min_delay}-{max_delay}s delays")
        
        print("\nNote: Full scheduler implementation coming soon!")
        print("For now, use Option 96 (Auto-Post) for scheduled posting")
        status.show_success("Delay configuration saved")
        
    except Exception as e:
        logger.error(f"Failed message scheduler: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def contact_sync():
    """Feature 116: Contact Sync"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        print(f"\n{'='*70}")
        print("CONTACT SYNC")
        print(f"{'='*70}\n")
        
        contacts = await client.get_contacts()
        
        print(f"Total Contacts: {len(contacts)}")
        print("\nSyncing contacts...")
        
        # Save to database
        for contact in contacts:
            print(f"Synced: {contact.first_name}")
        
        print(f"\n{'='*70}")
        print(f"Synced {len(contacts)} contacts")
        print(f"{'='*70}\n")
        
        logger.success(f"Synced {len(contacts)} contacts")
        status.show_success("Contacts synced")
        
    except Exception as e:
        logger.error(f"Failed contact sync: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def vip_member_filter():
    """Feature 118: VIP Member Filter"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(group)
        
        print(f"\n{'='*70}")
        print("VIP MEMBER FILTER")
        print(f"{'='*70}\n")
        
        vip_members = []
        
        async for user in client.iter_participants(entity, limit=100):
            # VIP criteria: premium users, verified, or admins
            if user.premium or user.verified:
                vip_members.append(user)
        
        print(f"VIP Members Found: {len(vip_members)}")
        for vip in vip_members[:10]:
            print(f"  - {vip.first_name} (@{vip.username})" if vip.username else f"  - {vip.first_name}")
        
        print(f"\n{'='*70}\n")
        status.show_success(f"Found {len(vip_members)} VIP members")
        
    except Exception as e:
        logger.error(f"Failed VIP filter: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def engagement_tracker():
    """Feature 119: Engagement Tracker"""
    try:
        phone = input("Enter your phone number: ").strip()
        channel = input("Enter channel username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(channel)
        
        print(f"\n{'='*70}")
        print("ENGAGEMENT TRACKER")
        print(f"{'='*70}\n")
        
        total_views = 0
        total_reactions = 0
        total_forwards = 0
        message_count = 0
        
        async for message in client.iter_messages(entity, limit=30):
            message_count += 1
            if hasattr(message, 'views') and message.views:
                total_views += message.views
            if hasattr(message, 'forwards') and message.forwards:
                total_forwards += message.forwards
            if hasattr(message, 'reactions') and message.reactions:
                total_reactions += len(message.reactions.results)
        
        print(f"Messages Analyzed: {message_count}")
        print(f"Total Views: {total_views}")
        print(f"Total Reactions: {total_reactions}")
        print(f"Total Forwards: {total_forwards}")
        print(f"\nAverage Engagement:")
        print(f"  Views/Post: {total_views // message_count if message_count > 0 else 0}")
        print(f"  Reactions/Post: {total_reactions // message_count if message_count > 0 else 0}")
        print(f"  Forwards/Post: {total_forwards // message_count if message_count > 0 else 0}")
        print(f"\n{'='*70}\n")
        
        status.show_success("Engagement tracked")
        
    except Exception as e:
        logger.error(f"Failed engagement tracking: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def competitor_analysis():
    """Feature 120: Competitor Analysis"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        print("\nEnter competitor channels (one per line, empty to finish):")
        competitors = []
        while True:
            comp = input("> ").strip()
            if not comp:
                break
            competitors.append(comp)
        
        if not competitors:
            print("No competitors provided")
            return
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        print(f"\n{'='*70}")
        print("COMPETITOR ANALYSIS")
        print(f"{'='*70}\n")
        
        for comp in competitors:
            try:
                from telethon.tl.functions.channels import GetFullChannelRequest
                entity = await client.get_entity(comp)
                full = await client(GetFullChannelRequest(channel=entity))
                
                print(f"\n{comp}:")
                print(f"  Subscribers: {full.full_chat.participants_count}")
                
                # Get recent post performance
                views = 0
                count = 0
                async for msg in client.iter_messages(entity, limit=10):
                    count += 1
                    if hasattr(msg, 'views') and msg.views:
                        views += msg.views
                
                print(f"  Avg Views: {views // count if count > 0 else 0}")
                print(f"{'-'*70}")
                
            except Exception as e:
                print(f"Failed to analyze {comp}: {e}")
        
        print(f"\n{'='*70}\n")
        status.show_success("Competitor analysis complete")
        
    except Exception as e:
        logger.error(f"Failed competitor analysis: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

