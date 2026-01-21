"""
Additional Features Module
Bio update and other utilities
"""

import asyncio
from telethon.tl.functions.account import UpdateProfileRequest
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator
from utils.delay_manager import DelayManager
from utils.file_parser import FileParser

status = StatusIndicator()

async def update_bio_all_accounts():
    """
    Feature 123 (NEW): Update bio for all accounts
    """
    try:
        print(f"\n{'-'*70}")
        print("UPDATE BIO [ALL ACCOUNTS]")
        print(f"{'-'*70}\n")
        
        print("Bio Options:")
        print("1. Same bio for all accounts")
        print("2. Different bio per account (from file)")
        
        bio_choice = input("\nSelect option (1-2): ").strip()
        
        bios = {}
        
        if bio_choice == '1':
            # Same bio for all
            bio_text = input("Enter bio text: ").strip()
            
            # Get all accounts
            accounts = await db.get_all_accounts()
            for account in accounts:
                phone = account[1]
                bios[phone] = bio_text
        
        elif bio_choice == '2':
            # Different bio from file
            file_path = input("Enter path to bio file (format: phone,bio): ").strip()
            
            # Parse file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if ',' in line:
                            phone, bio = line.split(',', 1)
                            bios[phone.strip()] = bio.strip()
            except Exception as e:
                logger.error(f"Failed to parse bio file: {e}")
                return
        
        if not bios:
            status.show_error("No bios to update")
            return
        
        print(f"\n{'-'*70}")
        print(f"Accounts to Update: {len(bios)}")
        print(f"Delay: 30-60 seconds between accounts")
        print(f"{'-'*70}\n")
        
        confirm = input("Update bios? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        # Start updating
        total_updated = 0
        total_failed = 0
        
        for phone, bio in bios.items():
            try:
                client = await session_manager.get_client(phone)
                if not client:
                    logger.warning(f"Skipping {phone} - not connected")
                    total_failed += 1
                    continue
                
                # Update bio
                await client(UpdateProfileRequest(about=bio))
                
                logger.success(f"{phone} bio updated")
                total_updated += 1
                
                # Delay (30-60 seconds)
                await DelayManager.wait('bio_update')
                
            except Exception as e:
                logger.error(f"{phone} failed to update bio: {e}")
                total_failed += 1
        
        print(f"\n{'-'*70}")
        print(f"BIO UPDATE COMPLETED")
        print(f"{'-'*70}")
        print(f"Total Updated: {total_updated}")
        print(f"Total Failed: {total_failed}")
        print(f"{'-'*70}\n")
        
        status.show_success(f"Updated {total_updated} bios")
        
    except Exception as e:
        logger.error(f"Bio update error: {e}")
