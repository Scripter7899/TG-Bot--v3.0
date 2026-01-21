"""
System Operations Module
System-level features and workflows
"""

import asyncio
import os
import config
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator

status = StatusIndicator()

async def automated_workflows():
    """Feature 121: Automated Workflows & Background Task Management"""
    try:
        print(f"\n{'='*70}")
        print("AUTOMATED WORKFLOWS & BACKGROUND TASKS")
        print(f"{'='*70}\n")
        
        print("Options:")
        print("1. View Running Background Tasks")
        print("2. Stop Background Task")
        print("3. Configure Workflow (Coming Soon)")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            # View running tasks
            from core.background_tasks import background_tasks
            
            print(f"\n{'='*70}")
            print("RUNNING BACKGROUND TASKS")
            print(f"{'='*70}\n")
            
            tasks_list = background_tasks.list_tasks()
            
            if not tasks_list:
                print("No background tasks running")
            else:
                for task_info in tasks_list:
                    print(f"  • {task_info}")
            
            print(f"\n{'='*70}\n")
        
        elif choice == '2':
            # Stop a task
            from core.background_tasks import background_tasks
            
            print(f"\n{'='*70}")
            print("STOP BACKGROUND TASK")
            print(f"{'='*70}\n")
            
            tasks_list = background_tasks.list_tasks()
            
            if not tasks_list:
                print("No background tasks running")
            else:
                print("Running tasks:")
                for i, task_info in enumerate(tasks_list, 1):
                    print(f"  {i}. {task_info}")
                
                print("\nKnown task names:")
                print("  - auto_post_recurring (Option 96 recurring posts)")
                
                task_name = input("\nEnter task name to stop: ").strip()
                
                if background_tasks.stop_task(task_name):
                    print(f"\n✅ Task '{task_name}' stopped successfully")
                    logger.success(f"Stopped background task: {task_name}")
                else:
                    print(f"\n❌ Task '{task_name}' not found or already stopped")
            
            print(f"\n{'='*70}\n")
        
        elif choice == '3':
            print("\nWorkflow Configuration:")
            print("1. Daily Member Invite (20 members/day)")
            print("2. Auto-Post Schedule (3 posts/day)")
            print("3. Engagement Boost (react + comment)")
            print("4. Member Scraping (hourly)")
            print("5. Account Health Check (daily)")
            
            workflow_choice = input("\nSelect workflow (1-5): ").strip()
            
            if workflow_choice == '1':
                print("\nDaily Member Invite Workflow:")
                print("  - Scrape 50 members")
                print("  - Invite 20 members")
                print("  - 5-minute delays")
                print("  - Runs at 10 AM daily")
                
            elif workflow_choice == '2':
                print("\nAuto-Post Schedule Workflow:")
                print("  - 3 posts per day")
                print("  - 8 AM, 2 PM, 8 PM")
                print("  - Pulls from content queue")
                
            elif workflow_choice == '3':
                print("\nEngagement Boost Workflow:")
                print("  - React to new posts")
                print("  - Comment on trending posts")
                print("  - Share top content")
                
            elif workflow_choice == '4':
                print("\nMember Scraping Workflow:")
                print("  - Scrape every hour")
                print("  - Export to CSV")
                print("  - Deduplicate members")
                
            elif workflow_choice == '5':
                print("\nAccount Health Check Workflow:")
                print("  - Check restrictions")
                print("  - Verify sessions")
                print("  - Test connections")
            
            print("\n⚠️  Workflow configuration coming in future update!")
            logger.info("Workflow configuration requested")
        
        status.show_success("Operation completed")
        
    except Exception as e:
        logger.error(f"Failed workflow operation: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def reload_sessions():
    """Feature 122: Reload Sessions"""
    try:
        print(f"\n{'='*70}")
        print("RELOAD SESSIONS")
        print(f"{'='*70}\n")
        
        print("Reloading all sessions...")
        
        # Get all accounts
        accounts = await db.get_all_accounts()
        
        reloaded = 0
        failed = 0
        
        for account in accounts:
            try:
                phone = account[1]
                client = await session_manager.get_client(phone)
                
                if client:
                    if not client.is_connected():
                        await client.connect()
                    
                    # Test connection
                    await client.get_me()
                    print(f"✅ Reloaded: {phone}")
                    reloaded += 1
                else:
                    print(f"❌ Failed: {phone}")
                    failed += 1
                    
            except Exception as e:
                print(f"❌ Error {phone}: {e}")
                failed += 1
        
        print(f"\n{'='*70}")
        print(f"Reloaded: {reloaded} | Failed: {failed}")
        print(f"{'='*70}\n")
        
        logger.success(f"Reloaded {reloaded} sessions")
        status.show_success(f"Reloaded {reloaded} sessions")
        
    except Exception as e:
        logger.error(f"Failed to reload sessions: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def deep_system_cleanup():
    """Feature 128: Deep System Cleanup (Sync DB + Files)"""
    try:
        print(f"\n{'='*70}")
        print("DEEP SYSTEM CLEANUP")
        print(f"{'='*70}\n")
        
        print("This operation will:")
        print("1. Sync Database with Session Files")
        print("2. Remove DB entries for missing sessions")
        print("3. Clean up temporary files")
        
        confirm = input("\nProceed with deep cleanup? (yes/no): ").strip().lower()
        if confirm != 'yes':
            return

        status.show_processing("Syncing Database...")
        
        # 1. Database Sync
        accounts = await db.get_all_accounts(status='active')
        session_files = list(config.SESSIONS_DIR.glob("*.session"))
        session_map = {f.stem: f for f in session_files}
        
        to_remove = []
        for account in accounts:
            phone = account[1]
            expected_name = phone.replace('+', '')
            if expected_name not in session_map:
                to_remove.append(phone)
        
        removed_count = 0
        if to_remove:
            print(f"\nFound {len(to_remove)} orphaned accounts in DB.")
            for phone in to_remove:
                await db.remove_account(phone, "Deep Cleanup - Missing File")
                removed_count += 1
                print(f"  - Removed: {phone}")
        else:
            print("\nDatabase is in sync.")
            
        # 2. Temp File Cleanup
        status.show_processing("Cleaning temp files...")
        temp_cleaned = 0
        try:
            # Clean __pycache__ in modules
            import shutil
            for root, dirs, files in os.walk(config.BASE_DIR):
                for d in dirs:
                    if d == "__pycache__":
                        shutil.rmtree(os.path.join(root, d))
                        temp_cleaned += 1
        except Exception as e:
            logger.warning(f"Temp cleanup warning: {e}")

        print(f"\n{'='*70}")
        print("CLEANUP COMPLETE")
        print(f"{'='*70}")
        print(f"Orphaned Accounts Removed: {removed_count}")
        print(f"Temp Folders Cleaned: {temp_cleaned}")
        print(f"{'='*70}\n")
        
        logger.success("Deep system cleanup completed")
        status.show_success("System cleanup complete")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

