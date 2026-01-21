import os
import shutil
import sqlite3
import re
from pathlib import Path
from datetime import datetime

# Configuration
SOURCE_DIR = Path("New Sessions [TG-Bot]")
DEST_DIR = Path("sessions")
DB_PATH = Path("data/database.db")
BACKUP_DIR = Path("backups/pre_import_backup")

# API Credentials from .env (Hardcoded here for the script based on previous read)
API_ID = "26970168"
API_HASH = "45623e74fdea675058c6ceb2c5e70342"

def setup_backup():
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)
    
    # Backup DB
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, BACKUP_DIR / "database.db")
        print(f"Backed up database to {BACKUP_DIR}")

    # Backup Sessions
    if DEST_DIR.exists():
        shutil.make_archive(str(BACKUP_DIR / "sessions_backup"), 'zip', DEST_DIR)
        print(f"Backed up sessions to {BACKUP_DIR}")

def import_sessions(clear_existing=False):
    if not SOURCE_DIR.exists():
        print(f"Source directory {SOURCE_DIR} not found!")
        return

    if not DEST_DIR.exists():
        DEST_DIR.mkdir(parents=True)

    # Database connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure tables exist (in case DB is fresh)
    # We assume schema exists or DB is valid. If not, we might error. 
    # But usually app creates it. We'll proceed assuming DB exists or app runs first.

    if clear_existing:
        print("Clearing existing sessions and database records...")
        # Clear DB
        cursor.execute("DELETE FROM accounts")
        conn.commit()
        # Clear folder
        for item in DEST_DIR.glob("*"):
            if item.is_file():
                item.unlink()
        print("Existing data cleared.")

    files = list(SOURCE_DIR.glob("*.session"))
    print(f"Found {len(files)} session files to import.")

    imported_count = 0
    for file_path in files:
        # Expected format: {phone}.session
        filename = file_path.name
        # Match digits only for phone
        phone_match = re.search(r'(\d+)', filename)
        
        if not phone_match:
            print(f"Skipping {filename}: Could not extract phone number")
            continue
            
        phone_number = phone_match.group(1)
        # Ensure it has + prefix if not present (Telethon usually likes full format, but app uses raw digits in filename mostly)
        # Looking at existing: session_27613140018.session. The phone in DB usually has +.
        # But let's check consistent phone storage. 
        # App's session_manager: session_name = f"session_{phone.replace('+', '')}"
        # So filename uses digits. DB uses phone (likely with +).
        
        if not phone_number.startswith('+'):
            db_phone = f"+{phone_number}"
        else:
            db_phone = phone_number
            phone_number = phone_number.replace('+', '')

        new_filename = f"{phone_number}.session"
        dest_path = DEST_DIR / new_filename

        # Copy file
        shutil.copy2(file_path, dest_path)

        # Insert into DB
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO accounts (phone, session_name, api_id, api_hash, status, last_used)
                VALUES (?, ?, ?, ?, 'active', ?)
            """, (db_phone, f"{phone_number}", API_ID, API_HASH, datetime.now()))
            imported_count += 1
            print(f"Imported {db_phone}")
        except sqlite3.Error as e:
            print(f"Error registering {db_phone}: {e}")

    conn.commit()
    conn.close()
    print(f"\nSuccessfully imported {imported_count} sessions.")

if __name__ == "__main__":
    print("Starting session import...")
    setup_backup()
    
    # We will Default to REPLACING/MERGING. 
    # Since the user wants to use the NEW sessions, we perform the import.
    # We won't strictly clear existing unless requested, but INSERT OR REPLACE handles overlap.
    # However, if user wants ONLY new sessions, they can ask to clear.
    # For now, we merge.
    
    import_sessions(clear_existing=False) 
