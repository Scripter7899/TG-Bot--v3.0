"""
Statistics Operations Module
Statistics and analytics features
"""

import asyncio
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator
import config

status = StatusIndicator()

async def account_statistics():
    """Feature 72: Account Statistics"""
    try:
        phone = input("Enter phone number: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        # Get dialogs
        dialogs = await client.get_dialogs()
        groups = sum(1 for d in dialogs if d.is_group)
        channels = sum(1 for d in dialogs if d.is_channel)
        users = sum(1 for d in dialogs if d.is_user)
        
        # Get account info
        me = await client.get_me()
        
        # Get database stats
        account_data = await db.get_account(phone)
        
        print(f"\n{'='*70}")
        print(f"ACCOUNT STATISTICS: {phone}")
        print(f"{'='*70}")
        print(f"Name: {me.first_name} {me.last_name or ''}")
        print(f"Username: @{me.username}" if me.username else "No username")
        print(f"User ID: {me.id}")
        print(f"Premium: {'Yes' if me.premium else 'No'}")
        print(f"\nDialogs:")
        print(f"  Total: {len(dialogs)}")
        print(f"  Groups: {groups}")
        print(f"  Channels: {channels}")
        print(f"  Private Chats: {users}")
        print(f"\nAccount Status:")
        print(f"  Status: {account_data[6] if account_data else 'Unknown'}")
        print(f"  Last Used: {account_data[7] if account_data else 'Never'}")
        print(f"{'='*70}\n")
        
        status.show_success("Statistics retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get account statistics: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def invite_statistics():
    """Feature 75: Invite Statistics"""
    try:
        print(f"\n{'='*70}")
        print("INVITE STATISTICS")
        print(f"{'='*70}\n")
        
        # Read logs
        added_count = 0
        error_count = 0
        
        if config.ADDED_USERS_LOG.exists():
            with open(config.ADDED_USERS_LOG, 'r', encoding='utf-8') as f:
                added_count = len(f.readlines())
        
        if config.ERROR_USERS_LOG.exists():
            with open(config.ERROR_USERS_LOG, 'r', encoding='utf-8') as f:
                error_count = len(f.readlines())
        
        total_attempts = added_count + error_count
        success_rate = (added_count / total_attempts * 100) if total_attempts > 0 else 0
        
        print(f"Total Invite Attempts: {total_attempts}")
        print(f"Successfully Added: {added_count}")
        print(f"Failed/Errors: {error_count}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"\n{'='*70}\n")
        
        status.show_success("Invite statistics retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get invite statistics: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def session_storage_info():
    """Feature 84: Session Storage Info"""
    try:
        import os
        
        print(f"\n{'='*70}")
        print("SESSION STORAGE INFORMATION")
        print(f"{'='*70}\n")
        
        # Get session files
        session_files = list(config.SESSIONS_DIR.glob("*.session"))
        
        total_size = 0
        for session_file in session_files:
            size = session_file.stat().st_size
            total_size += size
        
        print(f"Sessions Directory: {config.SESSIONS_DIR}")
        print(f"Total Sessions: {len(session_files)}")
        print(f"Total Size: {total_size / 1024:.2f} KB")
        print(f"Average Size: {(total_size / len(session_files) / 1024):.2f} KB" if session_files else "0 KB")
        
        print(f"\nSession Files:")
        for idx, session_file in enumerate(session_files[:10], 1):
            size = session_file.stat().st_size / 1024
            print(f"  {idx}. {session_file.name}: {size:.2f} KB")
        
        if len(session_files) > 10:
            print(f"  ... and {len(session_files) - 10} more")
        
        print(f"\n{'='*70}\n")
        status.show_success("Session storage info retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get session storage info: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def proxy_statistics():
    """Feature 87: Proxy Statistics"""
    try:
        from core.proxy_manager import proxy_manager
        
        print(f"\n{'='*70}")
        print("PROXY STATISTICS")
        print(f"{'='*70}\n")
        
        # Get proxy stats
        proxies = await proxy_manager.get_all_proxies()
        
        print(f"Total Proxies: {len(proxies)}")
        
        if proxies:
            print(f"\nProxy List:")
            for idx, proxy in enumerate(proxies[:10], 1):
                print(f"  {idx}. {proxy['host']}:{proxy['port']} ({proxy['type']})")
            
            if len(proxies) > 10:
                print(f"  ... and {len(proxies) - 10} more")
        else:
            print("\nNo proxies configured")
        
        print(f"\n{'='*70}\n")
        status.show_success("Proxy statistics retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get proxy statistics: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def device_info():
    """Feature 88: Device Info"""
    try:
        import platform
        import psutil
        
        print(f"\n{'='*70}")
        print("DEVICE INFORMATION")
        print(f"{'='*70}\n")
        
        print(f"System: {platform.system()} {platform.release()}")
        print(f"Machine: {platform.machine()}")
        print(f"Processor: {platform.processor()}")
        print(f"Python Version: {platform.python_version()}")
        
        print(f"\nMemory:")
        memory = psutil.virtual_memory()
        print(f"  Total: {memory.total / (1024**3):.2f} GB")
        print(f"  Available: {memory.available / (1024**3):.2f} GB")
        print(f"  Used: {memory.percent}%")
        
        print(f"\nDisk:")
        disk = psutil.disk_usage('/')
        print(f"  Total: {disk.total / (1024**3):.2f} GB")
        print(f"  Free: {disk.free / (1024**3):.2f} GB")
        print(f"  Used: {disk.percent}%")
        
        print(f"\nCPU:")
        print(f"  Cores: {psutil.cpu_count()}")
        print(f"  Usage: {psutil.cpu_percent()}%")
        
        print(f"\n{'='*70}\n")
        status.show_success("Device info retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get device info: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

