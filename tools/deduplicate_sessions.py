
import asyncio
import sys
import os
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.database import db

async def get_existing_phones():
    """Get list of phone numbers already in the database"""
    print("Fetching existing accounts from database...")
    await db.connect()
    accounts = await db.get_all_accounts()
    # accounts is list of tuples, phone is usually index 1 (id, phone, ...)
    # Let's verify structure or just fetch phones directly if possible.
    # Looking at AccountHealthChecker it used account[1] for phone.
    existing_phones = set()
    for acc in accounts:
        if acc[1]:
            # Normalize phone: remove + and spaces
            phone = acc[1].replace('+', '').replace(' ', '').strip()
            existing_phones.add(phone)
    await db.close()
    return existing_phones

async def deduplicate():
    # 1. Get existing phones
    existing_phones = await get_existing_phones()
    print(f"Found {len(existing_phones)} existing accounts in database.")
    
    source_dir = Path("che sessions")
    if not source_dir.exists():
        print(f"Error: Directory '{source_dir}' not found.")
        return

    session_files = list(source_dir.glob("*.session"))
    print(f"Found {len(session_files)} session files in '{source_dir}'.")
    
    if not session_files:
        print("No sessions to check.")
        return

    duplicates_removed = 0
    errors = 0
    processed = 0

    print("\nChecking for duplicates...")
    
    for session_file in session_files:
        processed += 1
        try:
            # Telethon session name (path without extension)
            # We want to use the file in-place, not create new ones
            # session_file is absolute or relative path to .session file
            # TelegramClient expects path WITHOUT .session suffix
            session_path_str = str(session_file.with_suffix(''))
            
            client = TelegramClient(
                session_path_str,
                config.API_ID,
                config.API_HASH
            )
            
            async with client:
                # Check if authorized
                if not await client.is_user_authorized():
                    print(f"[{processed}/{len(session_files)}] ⚠ {session_file.name}: Not authorized/Invalid")
                    errors += 1
                    continue
                
                # Get account info
                try:
                    me = await client.get_me()
                    if not me:
                        print(f"[{processed}/{len(session_files)}] ⚠ {session_file.name}: Could not get account info")
                        errors += 1
                        continue
                        
                    phone = me.phone
                    if not phone:
                        print(f"[{processed}/{len(session_files)}] ⚠ {session_file.name}: No phone number found")
                        errors += 1
                        continue
                    
                    # Normalize checks
                    clean_phone = phone.replace('+', '').replace(' ', '').strip()
                    
                    if clean_phone in existing_phones:
                        # DUPLICATE FOUND
                        print(f"[{processed}/{len(session_files)}] 🗑 REMOVING DUPLICATE: {session_file.name} (Phone: +{clean_phone})")
                        
                        # Disconnect before deleting
                        await client.disconnect()
                        # Allow file handle release
                        await asyncio.sleep(0.2)
                        
                        # Delete file
                        try:
                            # client is closed due to async with, but let's be safe
                            pass
                        except:
                            pass
                            
                        # We need to close client specifically? 
                        # 'async with' handles disconnect, but sometimes not immediate file release on Windows
                    else:
                        print(f"[{processed}/{len(session_files)}] ✓ UNIQUE: {session_file.name} (Phone: +{clean_phone})")

                except Exception as e:
                    print(f"[{processed}/{len(session_files)}] ⚠ {session_file.name}: Error getting info: {e}")
                    errors += 1
                    
            # Outside async with, client is disconnected. Now safe to delete if marked?
            # Actually, inside the loop logic above, I identified it. 
            # I can't delete valid open file easily.
            # So I will check strict duplication logic again here.
            
            # Re-check and delete if it was a duplicate (need to store logic)
            # Let's refactor loop to just identify, then delete.
            pass

        except Exception as e:
            print(f"[{processed}/{len(session_files)}] ⚠ Error processing {session_file.name}: {e}")
            errors += 1

    # Better approach:
    # We can't delete "this" file while 'client' is using it in the block.
    # And we can't easily know if 'clean_phone' matched inside the 'async with' after it closes unless we store it.
    
    # Retry with safer delete logic
    
async def safe_deduplicate():
    existing_phones = await get_existing_phones()
    print(f"Found {len(existing_phones)} existing accounts in database.")
    
    source_dir = Path("che sessions")
    if not source_dir.exists():
        print("Folder not found.")
        return

    files = list(source_dir.glob("*.session"))
    print(f"Scanning {len(files)} files in {source_dir}...")
    
    files_to_delete = []

    for i, file_path in enumerate(files):
        try:
            # Connect
            client = TelegramClient(str(file_path.with_suffix('')), config.API_ID, config.API_HASH)
            phone_found = None
            is_duplicate = False
            
            try:
                await client.connect()
                if not await client.is_user_authorized():
                    # Invalid session, user didn't say delete, but maybe? 
                    # User said "remove duplicate".
                    pass
                else:
                    me = await client.get_me()
                    if me and me.phone:
                        phone_found = me.phone.replace('+', '').strip()
                        if phone_found in existing_phones:
                            is_duplicate = True
                        
            except Exception as e:
                # print(f"Error reading {file_path.name}: {e}")
                pass
            finally:
                await client.disconnect()
            
            # Now client is disconnected
            if is_duplicate:
                print(f"[{i+1}/{len(files)}] DUPLICATE FOUND: {file_path.name} -> +{phone_found}")
                files_to_delete.append(file_path)
            else:
                if phone_found:
                    print(f"[{i+1}/{len(files)}] Unique: {file_path.name} -> +{phone_found}")
                else:
                    print(f"[{i+1}/{len(files)}] Skipped (Invalid/Auth fail): {file_path.name}")
                    
        except Exception as e:
            print(f"Failed to process {file_path.name}: {e}")

    print(f"\nSummary: Found {len(files_to_delete)} duplicates to remove.")
    
    for file_path in files_to_delete:
        try:
            file_path.unlink()
            # Also journal
            journal = file_path.with_suffix('.session-journal')
            if journal.exists():
                journal.unlink()
            print(f"Deleted: {file_path.name}")
        except Exception as e:
            print(f"Failed to delete {file_path.name}: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(safe_deduplicate())
    except KeyboardInterrupt:
        pass
