import asyncio
import os
import shutil
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import db
import config

async def migrate_sessions():
    print(f"\n{'='*60}")
    print("📂 MIGRATING SESSION NAMES")
    print(f"Goal: 'session_1234.session' -> '1234.session'")
    print(f"{'='*60}\n")
    
    # Connect to DB
    await db.connect()
    
    # 1. Get all files
    files = list(config.SESSIONS_DIR.glob("session_*.session"))
    print(f"Found {len(files)} session files to migrate.")
    
    migrated_count = 0
    
    with open("migration_log.txt", "w", encoding="utf-8") as log:
        log.write("Migration started\n")
        
        for old_path in files:
            filename = old_path.name
            # Extract phone: session_9198765.session -> 9198765
            phone = filename.replace("session_", "").replace(".session", "")
            
            new_filename = f"{phone}.session"
            new_path = config.SESSIONS_DIR / new_filename
            
            try:
                # Rename .session file
                if not new_path.exists():
                    old_path.rename(new_path)
                    msg = f"✅ Renamed: {filename} -> {new_filename}"
                    print(msg)
                    log.write(msg + "\n")
                else:
                    msg = f"⚠️  Target exists, skipping file: {new_filename}"
                    print(msg)
                    log.write(msg + "\n")
                
                # Rename journal if exists
                old_journal = old_path.with_suffix('.session-journal')
                if old_journal.exists():
                    new_journal = new_path.with_suffix('.session-journal')
                    old_journal.rename(new_journal)
                
                # Update Database
                async with db.connection.cursor() as cursor:
                    await cursor.execute(
                        "UPDATE accounts SET session_name = ? WHERE phone = ? OR phone = ?", 
                        (phone, phone, "+" + phone)
                    )
                    await db.connection.commit()
                
                migrated_count += 1
                
            except Exception as e:
                msg = f"❌ Failed to migrate {filename}: {e}"
                print(msg)
                log.write(msg + "\n")

    print(f"\n{'='*60}")
    print(f"Migration Complete. Processed {migrated_count}/{len(files)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(migrate_sessions())
