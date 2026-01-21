"""
Utilities Module
Utility and helper features
"""

import asyncio
from core.logger import logger
from ui.progress import StatusIndicator
import config
from datetime import datetime
import json

status = StatusIndicator()

async def view_operation_history():
    """Feature 92: View Operation History"""
    try:
        print(f"\n{'='*70}")
        print("OPERATION HISTORY")
        print(f"{'='*70}\n")
        
        # Check for log files
        log_files = [
            (config.ADDED_USERS_LOG, "Added Users"),
            (config.ERROR_USERS_LOG, "Error Users"),
            (config.LOGS_DIR / "operations.log", "Operations")
        ]
        
        for log_file, log_name in log_files:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"{log_name} Log: {len(lines)} entries")
                    if lines:
                        print(f"  Latest: {lines[-1].strip()}")
            else:
                print(f"{log_name} Log: No entries")
            print(f"{'-'*70}")
        
        print(f"\n{'='*70}\n")
        status.show_success("Operation history retrieved")
        
    except Exception as e:
        logger.error(f"Failed to view operation history: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def settings():
    """Feature 93: Settings"""
    try:
        print(f"\n{'='*70}")
        print("FULL-TG SETTINGS")
        print(f"{'='*70}\n")
        
        print("Current Configuration:")
        print(f"  API ID: {config.API_ID}")
        print(f"  API Hash: {'*' * 20}")
        print(f"  Sessions Directory: {config.SESSIONS_DIR}")
        print(f"  Logs Directory: {config.LOGS_DIR}")
        print(f"  Exports Directory: {config.EXPORTS_DIR}")
        print(f"  Database: {config.DATABASE_PATH}")
        
        print(f"\n{'-'*70}")
        print("Settings Options:")
        print("1. View Full Config")
        print("2. Clear All Logs")
        print("3. Backup Database")
        print("4. Reset Settings")
        print("0. Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            print(f"\nFull Configuration:")
            print(f"  API_ID: {config.API_ID}")
            print(f"  API_HASH: {config.API_HASH}")
            print(f"  SESSIONS_DIR: {config.SESSIONS_DIR}")
            print(f"  LOGS_DIR: {config.LOGS_DIR}")
            print(f"  EXPORTS_DIR: {config.EXPORTS_DIR}")
            print(f"  DATABASE_PATH: {config.DATABASE_PATH}")
            
        elif choice == '2':
            confirm = input("Clear all logs? (yes/no): ").strip().lower()
            if confirm == 'yes':
                for log_file in config.LOGS_DIR.glob("*.log"):
                    log_file.unlink()
                print("All logs cleared")
                logger.success("Logs cleared")
            
        elif choice == '3':
            backup_path = config.DATABASE_PATH.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            import shutil
            shutil.copy2(config.DATABASE_PATH, backup_path)
            print(f"Database backed up to: {backup_path}")
            logger.success(f"Database backed up")
            
        elif choice == '4':
            print("Reset settings feature not implemented")
        
        print(f"\n{'='*70}\n")
        status.show_success("Settings accessed")
        
    except Exception as e:
        logger.error(f"Failed to access settings: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")
