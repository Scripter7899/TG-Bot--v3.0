
import os
import glob
from pathlib import Path
import re

SESSION_DIR = Path("sessions")
LOG_FILE = Path("logs/removed_accounts.log")

def get_removed_phones():
    phones = set()
    if not LOG_FILE.exists():
        return phones
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            # Format: [Timestamp] Removed: +123456 - Reason: ...
            match = re.search(r'Removed: (\+\d+)', line)
            if match:
                phone = match.group(1).replace('+', '').strip()
                phones.add(phone)
    return phones

def force_cleanup():
    print("Starting forceful cleanup...")
    
    # 1. Delete files based on removed logs
    removed_phones = get_removed_phones()
    print(f"Found {len(removed_phones)} unique removed accounts in logs.")
    
    for phone in removed_phones:
        # Standard session
        target = SESSION_DIR / f"{phone}.session"
        if target.exists():
            try:
                target.unlink()
                print(f"Deleted removed account file: {target.name}")
            except Exception as e:
                print(f"Error deleting {target.name}: {e}")
        
        # Journal
        journal = SESSION_DIR / f"{phone}.session-journal"
        if journal.exists():
            try:
                journal.unlink()
                print(f"Deleted journal: {journal.name}")
            except Exception:
                pass

    # 2. Delete any .deleted or .garbage files
    garbage_patterns = ["*.session.deleted*", "*.session.garbage*"]
    for pattern in garbage_patterns:
        for garbage in SESSION_DIR.glob(pattern):
            try:
                garbage.unlink()
                print(f"Deleted garbage file: {garbage.name}")
            except Exception as e:
                print(f"Error deleting garbage {garbage.name}: {e}")

    print("Cleanup complete.")

if __name__ == "__main__":
    force_cleanup()
