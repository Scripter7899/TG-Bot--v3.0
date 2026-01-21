"""
FULL-TG v3.0 - Main Application
Comprehensive Telegram Automation Tool with 120+ Features

Author: @MR_DIAZZZ
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.database import db
from core.session_manager import session_manager
from core.proxy_manager import proxy_manager
from core.logger import logger
from ui.menu import show_menu, get_user_choice, show_feature_not_implemented, clear_screen, print_banner
from ui.colors import *

# Import feature modules
from modules.account_manager import *
from modules.multi_account import *
from modules.account_health import check_accounts_health, view_removed_accounts_log
from modules.all_features import *
from modules.enhanced_broadcast import broadcast_channel_post
from modules.fraud_reporting import report_scam_user
from modules.auto_reactions import auto_react_to_posts
from modules.auto_posting import auto_post_to_groups
from modules.engagement_booster import engagement_booster
from modules.auto_reply_bot import auto_reply_bot
from modules.post_reactor import react_to_post_with_all_accounts
from modules.additional_features import update_bio_all_accounts
from modules.channel_operations import join_channels_all_accounts
from modules.user_operations import *
from modules.messaging_operations import *
from modules.group_operations import *
from modules.reporting_operations import *
from modules.statistics_operations import *
from modules.story_operations import *
from modules.spam_operations import *
from modules.utilities import *
from modules.marketing_advanced import *
from modules.advanced_features import *
from modules.system_operations import *
from modules.view_booster import increase_view_count
from modules.combo_manager import run_option_126, run_option_127

async def initialize():
    """Initialize application"""
    try:
        logger.info("Initializing FULL-TG v3.0...")
        
        # Validate configuration
        is_valid, errors = config.validate_config()
        if not is_valid:
            logger.error("Configuration errors:")
            for error in errors:
                logger.error(f"  - {error}")
            logger.info("\nPlease copy .env.example to .env and configure your API credentials")
            logger.info("Get API credentials from: https://my.telegram.org")
            return False
        
        # Connect to database
        await db.connect()
        logger.success("Database connected")
        
        # Load proxies
        await proxy_manager.load_proxies()
        logger.info(f"Loaded {proxy_manager.get_proxy_count()} proxies")
        
        # Load existing sessions
        loaded = await session_manager.load_all_sessions()
        logger.info(f"Loaded {loaded} session(s)")
        
        # Auto health check if enabled
        if config.AUTO_HEALTH_CHECK and loaded > 0:
            logger.info("Running automatic health check...")
            from modules.account_health import health_checker
            await health_checker.check_all_accounts(auto_remove=True)
        
        # Show initializing message
        if loaded > 0:
            logger.info("Initializing background services...")
        
        logger.success("Initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return False

async def cleanup():
    """Cleanup before exit"""
    try:
        logger.info("Cleaning up...")
        await session_manager.disconnect_all()
        await db.close()
        logger.success("Cleanup complete")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

async def handle_feature(choice):
    """Handle feature selection"""
    try:
        # Account Management (1-10)
        if choice == 1:
            await login_new_account()
        elif choice == 2:
            await get_account_info()
        elif choice == 3:
            await change_profile_name()
        elif choice == 4:
            await update_profile_picture()
        elif choice == 5:
            await set_bio_status()
        elif choice == 6:
            await set_username()
        elif choice == 7:
            await view_2fa_status()
        elif choice == 8:
            await terminate_other_sessions()
        elif choice == 9:
            await view_active_sessions()
        elif choice == 10:
            await logout_account()
        
        # Proxy Management (11-13)
        elif choice == 11:
            await add_proxy_feature()
        elif choice == 12:
            await list_all_proxies()
        elif choice == 13:
            await rotate_proxy_feature()
        
        # Multi-Account Operations (14-18)
        elif choice == 14:
            await mass_invite_all_accounts()
        elif choice == 15:
            await broadcast_channel_post()  # Enhanced broadcast
        elif choice == 16:
            await join_groups_all_accounts()
        elif choice == 17:
            await leave_groups_all_accounts()
        elif choice == 18:
            await show_all_active_accounts()
        
        # Session Management (19-21)
        elif choice == 19:
            await list_all_sessions()
        elif choice == 20:
            await delete_session_feature()
        elif choice == 21:
            await smart_clone_session()
        
        # User Operations (22-30)
        elif choice == 22:
            await get_user_full_info()
        elif choice == 23:
            await add_contact()
        elif choice == 24:
            await block_user()
        elif choice == 25:
            await unblock_user()
        elif choice == 26:
            await find_user()
        elif choice == 27:
            await get_mutual_friends()
        elif choice == 28:
            await get_last_seen()
        elif choice == 29:
            await get_user_followers()
        elif choice == 30:
            await get_user_channels()
        
        # Messaging Operations (31-45)
        elif choice == 31: await send_direct_message()
        elif choice == 32: await send_media()
        elif choice == 33: await forward_messages()
        elif choice == 34: await edit_message()
        elif choice == 35: await delete_messages()
        elif choice == 36: await search_messages()
        elif choice == 37: await pin_message()
        elif choice == 38: await unpin_message()
        elif choice == 39: await react_to_post_with_all_accounts()
        elif choice == 40: await get_message_info()
        elif choice == 41: await view_message_stats()
        elif choice == 42: await get_message_link()
        elif choice == 43: await schedule_message()
        elif choice == 44: await bulk_delete()
        elif choice == 45: await message_analytics()
        
        # Group Operations (46-60)
        elif choice == 46: await create_group()
        elif choice == 47: await export_members()
        elif choice == 48: await add_members()
        elif choice == 49: await group_statistics()
        elif choice == 50: await get_group_link()
        elif choice == 51: await change_group_title()
        elif choice == 52: await change_group_description()
        elif choice == 53: await get_member_info()
        elif choice == 54:
            await mute_user()
        elif choice == 55:
            await unmute_user()
        elif choice == 56:
            await kick_user()
        elif choice == 57:
            await make_admin()
        elif choice == 58:
            await remove_admin()
        elif choice == 59:
            await lock_group()
        elif choice == 60:
            await unlock_group()
        
        # Reporting (61-70) - RENUMBERED
        elif choice == 61:
            await report_group()
        elif choice == 62:
            await report_message()
        elif choice == 63:
            await clear_chat_history()
        elif choice == 64:
            await restrict_user()
        elif choice == 65:
            await mute_user_forever()
        elif choice == 66:
            await spam_report()
        elif choice == 67:
            await content_report()
        elif choice == 68:
            await bot_report()
        elif choice == 69:
            await report_scam_user()
        elif choice == 70:
            await advanced_report()
        
        # Story Operations (71-75)
        elif choice == 71:
            await view_stories()
        elif choice == 72:
            await post_story()
        elif choice == 73:
            await delete_story()
        elif choice == 74:
            await story_analytics()
        elif choice == 75:
            await download_stories()
        
        # Spam Operations (76-81)
        elif choice == 76:
            await mass_report()
        elif choice == 77:
            await auto_report_spam()
        elif choice == 78:
            await spam_filter()
        elif choice == 79:
            await block_spam_users()
        elif choice == 80:
            await report_fake_accounts()
        elif choice == 81:
            await anti_spam_monitor()
        
        # Statistics (82-88) - RENUMBERED
        elif choice == 82:
            await show_dialog_count()
        elif choice == 83:
            await account_statistics()
        elif choice == 84:
            await session_storage_info()
        elif choice == 85:
            await view_operation_logs()
        elif choice == 86:
            await invite_statistics()
        elif choice == 87:
            await proxy_statistics()
        elif choice == 88:
            await device_info()
        
        # Utilities (89-95) - RENUMBERED
        elif choice == 89:
            await view_added_users_log()
        elif choice == 90:
            await view_error_users_log()
        elif choice == 91:
            await cleanup_old_logs()
        elif choice == 92:
            await view_operation_history()
        elif choice == 93:
            await settings()
        elif choice == 94:
            await show_about()
        elif choice == 95:
            await check_accounts_health()
        
        # Marketing Operations (96-105) - RENUMBERED
        elif choice == 96:
            await auto_post_to_groups()
        elif choice == 97:
            await auto_react_to_posts()
        elif choice == 98:
            await auto_comment_on_posts()
        elif choice == 99:
            await follow_recommendations()
        elif choice == 100:
            await channel_growth_analytics()
        elif choice == 101:
            await hashtag_management()
        elif choice == 102:
            await trending_topics_tracker()
        elif choice == 103:
            await schedule_posts()
        elif choice == 104:
            await engagement_booster()
        elif choice == 105:
            await content_optimizer()
        
        # Advanced Features (106-120) - RENUMBERED
        elif choice == 106:
            await push_updates_check_version()
        elif choice == 107:
            await auto_member_scraper()
        elif choice == 108:
            await smart_invite_ai()
        elif choice == 109:
            await backup_restore()
        elif choice == 110:
            await account_switcher()
        elif choice == 111:
            await message_scheduler()
        elif choice == 112:
            await auto_reply_bot()
        elif choice == 113:
            await media_bulk_downloader()
        elif choice == 114:
            await chat_exporter()
        elif choice == 115:
            await username_monitor()
        elif choice == 116:
            await contact_sync()
        elif choice == 117:
            await anti_ban_system()
        elif choice >= 118 and choice <= 120:
            if choice == 118:
                await vip_member_filter()
            elif choice == 119:
                await engagement_tracker()
            elif choice == 120:
                await competitor_analysis()
        
        # System (121-124) - RENUMBERED
        elif choice == 121:
            await automated_workflows()
        elif choice == 122:
            await reload_sessions()
        elif choice == 123:
            await update_bio_all_accounts()
        elif choice == 124:
            await join_channels_all_accounts()
        elif choice == 125:
            await increase_view_count()
        elif choice == 126:
            await run_option_126()
        elif choice == 127:
            await run_option_127()
        elif choice == 128:
            await deep_system_cleanup()
        
        else:
            print(f"{ERROR}Invalid option. Please try again.{RESET}")
        
    except (KeyboardInterrupt, asyncio.CancelledError):
        print(f"\n\n{WARNING}⚠️  Operation cancelled by user. Returning to menu...{RESET}")
    except Exception as e:
        logger.error(f"Feature error: {e}")
    
    try:
        input(f"\n{PROMPT}Press Enter to continue...{RESET}")
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass


async def main():
    """Main application loop"""
    try:
        # Initialize
        if not await initialize():
            logger.error("Failed to initialize. Exiting...")
            return
        
        # Main loop
        while True:
            try:
                clear_screen()
                print_banner()
                show_menu()
                
                choice = get_user_choice()
                
                if choice == 0:
                    print(f"\n{INFO}Exiting FULL-TG...{RESET}")
                    break
                elif choice == -1:
                    print(f"{ERROR}Invalid input. Please enter a number.{RESET}")
                    await asyncio.sleep(1)
                    continue
                
                await handle_feature(choice)
                
            except (KeyboardInterrupt, asyncio.CancelledError):
                print(f"\n\n{WARNING}Operation cancelled. Returning to menu...{RESET}")
                await asyncio.sleep(0.5)
                continue
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(2)
        
        # Cleanup
        await cleanup()
        
        print(f"\n{SUCCESS}Thank you for using FULL-TG v{config.APP_VERSION}!{RESET}")
        print(f"{INFO}Author: {config.APP_AUTHORS}{RESET}\n")
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        await cleanup()

if __name__ == "__main__":
    try:
        # Run the application
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{WARNING}Application terminated by user{RESET}")
    except Exception as e:
        print(f"\n{ERROR}Fatal error: {e}{RESET}")
