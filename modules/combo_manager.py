import asyncio
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator
from ui.colors import *
import config

# Import headless functions
from modules.engagement_booster import start_engagement_simulation
from modules.auto_reactions import start_auto_react_daemon
from modules.auto_reply_bot import start_auto_reply_daemon
from modules.auto_posting import auto_post_to_groups # Can run in recurrence mode, but needs config extraction if we want truly headless. 
# For now, Auto Post is complex to setup headless without full UI reimplementation.
# Strategy: We will ask user sequentially for setup, then run them together.

status = StatusIndicator()

async def run_option_126():
    """
    Feature 126: Engagement Booster + Auto React
    """
    print(f"\n{'-'*70}")
    print(f"{BOLD}⭐ COMBO OPTION 126: ENGAGEMENT + AUTO-REACT{RESET}")
    print(f"{'-'*70}\n")
    
    # 1. Setup Engagement Booster
    print(f"{INFO}--- SETUP: ENGAGEMENT BOOSTER ---{RESET}")
    print("Mode: Continuous (Recommended for Combo)")
    mode_choice = '1'
    duration_hours = None
    action_count = None
    
    print("\nActivity Intensity:")
    print("1. Low (1-3 actions per hour)")
    print("2. Medium (3-6 actions per hour)")
    print("3. High (6-10 actions per hour)")
    intensity = input("\nSelect intensity (1-3): ").strip()
    if intensity not in ['1', '2', '3']: intensity = '2'

    # 2. Setup Auto React
    print(f"\n{INFO}--- SETUP: AUTO-REACT ---{RESET}")
    groups = config.AUTO_REACT_CHANNELS
    if not groups:
        print(f"{ERROR}No channels configured in .env/config.py!{RESET}")
        return
    print(f"Channels loaded: {len(groups)}")

    # 3. Get Accounts
    clients_dict = await session_manager.get_all_clients()
    if not clients_dict:
        status.show_error("No active accounts found")
        return

    # 4. Confirmation
    print(f"\n{'-'*70}")
    print(f"Starting Combo Mode:")
    print(f"1. Engagement Booster (Intensity: {intensity})")
    print(f"2. Auto-React (Channels: {len(groups)})")
    print(f"Accounts: {len(clients_dict)}")
    print(f"{'-'*70}\n")
    
    confirm = input("Start All Features? (yes/no): ").strip().lower()
    if confirm != 'yes': return

    # 5. Launch Tasks
    logger.info("Starting Combo Features...")
    
    tasks = []
    
    # Task 1: Engagement
    tasks.append(asyncio.create_task(
        start_engagement_simulation(mode_choice, duration_hours, action_count, intensity, clients_dict)
    ))
    
    # Task 2: Auto React
    # Note: Auto React typically uses global listener client. 
    # start_auto_react_daemon takes (clients_dict item list, groups)
    active_clients_list = list(clients_dict.items())
    tasks.append(asyncio.create_task(
        start_auto_react_daemon(active_clients_list, groups)
    ))
    
    # Wait for completion (indefinite)
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Combo error: {e}")
    except KeyboardInterrupt:
        logger.info("Combo stopped by user")


async def run_option_127():
    """
    Feature 127: Engagement + Auto Post + Auto Reply
    """
    print(f"\n{'-'*70}")
    print(f"{BOLD}⭐ COMBO OPTION 127: ENGAGEMENT + POST + REPLY{RESET}")
    print(f"{'-'*70}\n")
    
    # 1. Setup Engagement
    print(f"{INFO}--- SETUP: ENGAGEMENT BOOSTER ---{RESET}")
    print("Mode: Continuous")
    intensity = input("Select intensity (1=Low, 2=Med, 3=High): ").strip()
    if intensity not in ['1', '2', '3']: intensity = '2'
    
    # 2. Setup Auto Reply
    print(f"\n{INFO}--- SETUP: AUTO-REPLY BOT ---{RESET}")
    print("1. Template responses")
    print("2. Custom away message")
    reply_mode = input("Select mode (1-2): ").strip()
    away_msg = None
    if reply_mode == '2':
        away_msg = input("Enter away message: ").strip()
        
    # 3. Setup Auto Post
    # Since Auto Post logic is complex to decouple fully without massive rewrite,
    # we will recommend user to set it up via 'Recurring Mode' first or 
    # we can implement a simplified headless poster here. 
    # For now, let's skip auto-post input complexity and implement simplified looping poster?
    # No, better to warn user or just skip complex setup.
    # OR: We just run engagement + reply for now as per "Smart way".
    # User asked for "Auto Post to Groups". 
    # Let's try to run the recurring task if it was already configured? 
    # Or just tell user "Auto Post acts as scheduled task".
    
    # Let's try to do a simplified setup for Auto Post here:
    print(f"\n{INFO}--- SETUP: AUTO-POST ---{RESET}")
    print("Configuring simplified auto-post...")
    content_text = input("Enter post text: ").strip()
    target_groups = [] # All text groups logic need to be replicated or imports.
    # For robust 127, we might need to fully import auto_posting ...
    
    # ... Actually, auto_posting.execute_post_cycle IS reusable!
    # We just need to wrap it in a loop.
    
    # Get Accounts
    clients_dict = await session_manager.get_all_clients()
    if not clients_dict:
        status.show_error("No active accounts found")
        return

    # Confirmation
    print(f"\n{'-'*70}")
    print(f"Starting Combo 127:")
    print(f"1. Engagement Booster")
    print(f"2. Auto-Reply Bot")
    print(f"3. Auto-Post (Text Mode to All Groups)")
    print(f"{'-'*70}\n")
    
    confirm = input("Start All Features? (yes/no): ").strip().lower()
    if confirm != 'yes': return
    
    logger.info("Starting Combo Features...")
    tasks = []
    
    # Task 1: Engagement
    tasks.append(asyncio.create_task(
        start_engagement_simulation('1', None, None, intensity, clients_dict)
    ))
    
    # Task 2: Auto Reply
    tasks.append(asyncio.create_task(
        start_auto_reply_daemon(clients_dict, reply_mode, away_msg)
    ))
    
    # Task 3: Auto Post Loop
    # We define a simple loop wrapper here
    from modules.auto_posting import execute_post_cycle
    async def auto_post_loop():
        while True:
            try:
                # Simplified: Text only, All groups, Default delays
                logger.info("Running Auto-Post Cycle...")
                await execute_post_cycle(
                    clients_dict, 
                    '1', # Content choice: Text
                    content_text, 
                    None, None, # File, URL
                    '1', # Target: All groups
                    [], # Target list
                    120, 300 # Delays
                )
                logger.success("Auto-Post Cycle Done. Waiting 1 hour...")
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"Auto-Post Loop error: {e}")
                await asyncio.sleep(60)

    tasks.append(asyncio.create_task(auto_post_loop()))
    
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Combo error: {e}")
    except KeyboardInterrupt:
        logger.info("Combo stopped")
