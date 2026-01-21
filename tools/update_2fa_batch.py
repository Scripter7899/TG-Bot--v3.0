
import asyncio
import sys
from telethon import errors

# Add project root to path
import os
sys.path.insert(0, os.getcwd())

from core.session_manager import session_manager
from core.database import db
from core.logger import logger

OLD_PASS = "118822"
NEW_PASS = "pass1234"

async def update_2fa_batch():
    print(f"\n{'='*60}")
    print("🔐 BATCH 2FA PASSWORD UPDATE")
    print(f"Goal: Change '{OLD_PASS}' -> '{NEW_PASS}'")
    print(f"{'='*60}\n")

    # Connect to DB first
    await db.connect()
    
    # Load sessions first
    print("Loading sessions from database...")
    await session_manager.load_all_sessions()

    # Get all clients
    clients_dict = await session_manager.get_all_clients()
    
    if not clients_dict:
        print("❌ No active sessions found in database.")
        print("💡 Hint: If sessions exist on disk but not in DB, run import_sessions.py")
        return

    print(f"Found {len(clients_dict)} active sessions. Starting update...\n")
    
    results = {
        "updated": [],
        "already_correct": [],
        "failed": [],
        "unknown_pass": []
    }

    for i, (phone, client) in enumerate(clients_dict.items(), 1):
        msg = f"Processing {i}/{len(clients_dict)}: {phone}..."
        print(msg, end=" ", flush=True)
        with open("debug_log.txt", "a") as f:
            f.write(msg + "\n")
            f.flush()
        
        try:
            if not client.is_connected():
                await client.connect()
            
            if not await client.is_user_authorized():
                print("❌ Not authorized")
                with open("debug_log.txt", "a") as f:
                    f.write(f"-> Not authorized\n")
                results["failed"].append(phone)
                continue

            # Try to update from OLD to NEW
            try:
                await client.edit_2fa(current_password=OLD_PASS, new_password=NEW_PASS)
                print(f"✅ UPDATED")
                with open("debug_log.txt", "a") as f:
                    f.write(f"-> UPDATED\n")
                results["updated"].append(phone)
            
            except errors.PasswordHashInvalidError:
                # 118822 didn't work. Check if it's already pass1234
                try:
                    await client.edit_2fa(current_password=NEW_PASS, new_password=NEW_PASS)
                    print(f"ℹ️  Already Correct")
                    with open("debug_log.txt", "a") as f:
                        f.write(f"-> Already Correct\n")
                    results["already_correct"].append(phone)
                except errors.PasswordHashInvalidError:
                    print(f"⚠️  Unknown Password")
                    with open("debug_log.txt", "a") as f:
                        f.write(f"-> Unknown Password\n")
                    results["unknown_pass"].append(phone)
                except Exception as e:
                    print(f"❌ Error checking: {e}")
                    with open("debug_log.txt", "a") as f:
                        f.write(f"-> Error checking: {e}\n")
                    results["failed"].append(phone)

            except Exception as e:
                print(f"❌ Error updating: {e}")
                with open("debug_log.txt", "a") as f:
                    f.write(f"-> Error updating: {e}\n")
                results["failed"].append(phone)

        except Exception as e:
            print(f"❌ Connection Error: {e}")
            with open("debug_log.txt", "a") as f:
                f.write(f"-> Connection Error: {e}\n")
            results["failed"].append(phone)

    # Report
    summary = []
    summary.append(f"\n{'='*60}")
    summary.append("📊 UPDATE REPORT")
    summary.append(f"{'='*60}")
    summary.append(f"✅ Updated:         {len(results['updated'])}  {results['updated']}")
    summary.append(f"ℹ️  Already Correct: {len(results['already_correct'])}  {results['already_correct']}")
    summary.append(f"⚠️  Unknown Pass:    {len(results['unknown_pass'])}  {results['unknown_pass']}")
    summary.append(f"❌ Failed:          {len(results['failed'])}  {results['failed']}")
    summary.append(f"{'='*60}\n")
    
    report_text = "\n".join(summary)
    print(report_text)
    
    with open("update_2fa_log.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

if __name__ == "__main__":
    try:
        with open("debug_log.txt", "w") as f:
            f.write("Script started\n")
        asyncio.run(update_2fa_batch())
    except Exception as e:
        with open("debug_log.txt", "a") as f:
            f.write(f"CRITICAL ERROR: {e}\n")
        print(f"CRITICAL ERROR: {e}")
