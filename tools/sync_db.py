
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.database import db
import config
from core.logger import logger

async def sync_database():
    print(f"\n{'='*70}")
    print("DATABASE SYNCHRONIZATION TOOL")
    print(f"{'='*70}\n")
    
    await db.connect()
    
    # Get all accounts from DB
    accounts = await db.get_all_accounts(status='active')
    print(f"Total Database Accounts: {len(accounts)}")
    
    # Get all physical session files
    session_files = list(config.SESSIONS_DIR.glob("*.session"))
    session_map = {f.stem: f for f in session_files}
    print(f"Total Session Files: {len(session_files)}")
    
    to_remove = []
    
    for account in accounts:
        phone = account[1] # Phone column
        # Session name in DB might be old format or just phone
        # We check if a file exists for this phone
        
        # Logic: 
        # 1. Check if direct phone match exists (919876543210.session)
        # 2. Check if DB session_name matches a file
        
        expected_name = phone.replace('+', '')
        if expected_name not in session_map:
            to_remove.append(phone)
    
    print(f"\nFound {len(to_remove)} accounts in DB without session files.")
    
    if to_remove:
        print("\nAccounts to remove:")
        for phone in to_remove[:10]:
            print(f"  - {phone}")
        if len(to_remove) > 10:
            print(f"  ...and {len(to_remove)-10} more")
            
        confirm = input("\nRemove these accounts from database? (yes/no): ").strip().lower()
        if confirm == 'yes':
            removed_count = 0
            for phone in to_remove:
                await db.remove_account(phone, "Sync Cleanup - File Missing")
                removed_count += 1
                print(f"Removed: {phone}")
            
            print(f"\nSuccessfully removed {removed_count} accounts.")
            logger.success(f"Database sync: Removed {removed_count} orphaned accounts")
        else:
            print("Operation cancelled.")
    else:
        print("\nDatabase is already in sync!")

    await db.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(sync_database())
