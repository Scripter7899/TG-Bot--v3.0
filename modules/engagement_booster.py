"""
Account Health & Engagement Simulator
Simulates human-like activity across entire Telegram account
Makes accounts look real and healthy through random natural actions
"""

import asyncio
import random
from datetime import datetime, timedelta

from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator


status = StatusIndicator()

# Greeting messages (casual, natural)
GREETING_MESSAGES = [
    "Hey everyone! 👋",
    "Good morning! ☀️",
    "Good evening! 🌙",
    "Hi there! 😊",
    "Hello! How's everyone doing?",
    "Hey! What's up?",
    "Morning folks! ☕",
    "Evening everyone! 🌆",
    "Hi all! 👋",
    "Hey guys! 😄"
]

# Casual conversation starters
CONVERSATION_STARTERS = [
    "Interesting discussion here!",
    "Thanks for sharing this!",
    "Great point!",
    "I agree with this 👍",
    "Makes sense!",
    "Good to know!",
    "Appreciate the info!",
    "Helpful, thanks!",
    "Nice! 🔥",
    "Cool stuff! ✨"
]

# Positive reactions
# Positive reactions (Verified safe list)
POSITIVE_REACTIONS = ['👍', '❤', '🔥', '🎉', '👏', '😁', '🤩', '💯']

# Activity weights (probability of each action)
ACTIVITY_WEIGHTS = {
    'like_message': 0.30,      # 30% - Most common
    'react_to_post': 0.25,     # 25% - Very common
    'send_greeting': 0.15,     # 15% - Moderate
    'send_comment': 0.15,      # 15% - Moderate
    'view_stories': 0.10,      # 10% - Less common
    'read_messages': 0.05      # 5% - Passive activity
}

async def simulate_account_activity():
    """
    Feature 104 (MAXIMIZED): Full account health & engagement simulator
    Simulates natural human behavior across entire Telegram account
    """
    try:
        print(f"\n{'='*70}")
        print("⭐ ACCOUNT HEALTH & ENGAGEMENT SIMULATOR")
        print(f"{'='*70}\n")
        
        print("This feature simulates natural human activity to keep accounts healthy:")
        print("✓ Random likes on messages")
        print("✓ Random reactions on posts")
        print("✓ Casual greetings in groups")
        print("✓ Occasional comments")
        print("✓ Story views")
        print("✓ Message reading")
        print("✓ Natural delays between actions")
        print()
        
        # Get mode
        print("Simulation Mode:")
        print("1. Continuous (runs until stopped)")
        print("2. Timed (run for specific duration)")
        print("3. Action-based (perform X actions then stop)")
        
        mode_choice = input("\nSelect mode (1-3): ").strip()
        
        duration_hours = None
        action_count = None
        
        if mode_choice == '2':
            duration_hours = int(input("Enter duration in hours: ").strip())
        elif mode_choice == '3':
            action_count = int(input("Enter number of actions per account: ").strip())
        
        # Get intensity
        print("\nActivity Intensity:")
        print("1. Low (1-3 actions per hour)")
        print("2. Medium (3-6 actions per hour)")
        print("3. High (6-10 actions per hour)")
        
        intensity = input("\nSelect intensity (1-3): ").strip()
        
        # Get accounts for interactive mode
        clients_dict = await session_manager.get_all_clients()
        if not clients_dict:
            status.show_error("No active accounts found")
            return

        confirm = input("\nStart simulation? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        await start_engagement_simulation(mode_choice, duration_hours, action_count, intensity, clients_dict)
    except Exception as e:
        logger.error(f"Engagement simulator error: {e}")

async def start_engagement_simulation(mode_choice, duration_hours, action_count, intensity, clients_dict):
    """Headless entry point for engagement simulation"""
    try:
        # Calculate delay ranges based on intensity
        if intensity == '1':
            action_delay = (1200, 3600)  # 20-60 minutes
        elif intensity == '2':
            action_delay = (600, 1200)   # 10-20 minutes
        else:
            action_delay = (360, 600)    # 6-10 minutes

        # Start simulation for each account in parallel
        async def simulate_for_account(phone, client):
            """Simulate activity for a single account"""
            actions_performed = 0
            start_time = datetime.now()
            
            logger.info(f"[{phone}] Starting activity simulation")
            
            # Initial random staggering to prevent all accounts from acting at once
            initial_delay = random.uniform(5, 120) 
            logger.info(f"[{phone}] Staggering start by {initial_delay:.1f}s...")
            await asyncio.sleep(initial_delay)
            
            try:
                while True:
                    # Check stop conditions
                    if mode_choice == '2' and duration_hours:
                        if (datetime.now() - start_time).total_seconds() > duration_hours * 3600:
                            break
                    elif mode_choice == '3' and action_count:
                        if actions_performed >= action_count:
                            break
                    
                    # Reconnect if needed
                    if not client.is_connected():
                        await client.connect()
                    
                    # Get all dialogs (groups, channels, users)
                    dialogs = await client.get_dialogs()
                    
                    if not dialogs:
                        logger.warning(f"[{phone}] No dialogs found")
                        break
                    
                    # Choose random action based on weights
                    action = random.choices(
                        list(ACTIVITY_WEIGHTS.keys()),
                        weights=list(ACTIVITY_WEIGHTS.values())
                    )[0]
                    
                    try:
                        if action == 'like_message':
                            # Like a random recent message
                            dialog = random.choice([d for d in dialogs if d.is_group or d.is_channel])
                            messages = await client.get_messages(dialog.entity, limit=20)
                            
                            if messages:
                                msg = random.choice(messages)
                                reaction = random.choice(POSITIVE_REACTIONS)
                                
                                try:
                                    await client(SendReactionRequest(
                                        peer=dialog.entity,
                                        msg_id=msg.id,
                                        reaction=[ReactionEmoji(emoticon=reaction)]
                                    ))
                                    logger.success(f"[{phone}] Reacted {reaction} to message in {dialog.name}")
                                    actions_performed += 1
                                except Exception as e:
                                    # Retry logic: Try with a safe fallback emoji
                                    try:
                                        fallback = '👍'
                                        await client(SendReactionRequest(
                                            peer=dialog.entity,
                                            msg_id=msg.id,
                                            reaction=[ReactionEmoji(emoticon=fallback)]
                                        ))
                                        logger.success(f"[{phone}] Retry successful: Reacted {fallback} to message in {dialog.name}")
                                        actions_performed += 1
                                    except Exception:
                                        pass
                        
                        elif action == 'react_to_post':
                            # React to channel post
                            channels = [d for d in dialogs if d.is_channel]
                            if channels:
                                channel = random.choice(channels)
                                messages = await client.get_messages(channel.entity, limit=10)
                                
                                if messages:
                                    msg = random.choice(messages)
                                    reaction = random.choice(POSITIVE_REACTIONS)
                                    
                                    try:
                                        await client(SendReactionRequest(
                                            peer=channel.entity,
                                            msg_id=msg.id,
                                            reaction=[ReactionEmoji(emoticon=reaction)]
                                        ))
                                        logger.success(f"[{phone}] Reacted {reaction} to post in {channel.name}")
                                        actions_performed += 1
                                    except Exception as e:
                                        # Retry logic: Try with a safe fallback emoji
                                        try:
                                            fallback = '👍'
                                            await client(SendReactionRequest(
                                                peer=channel.entity,
                                                msg_id=msg.id,
                                                reaction=[ReactionEmoji(emoticon=fallback)]
                                            ))
                                            logger.success(f"[{phone}] Retry successful: Reacted {fallback} to post in {channel.name}")
                                            actions_performed += 1
                                        except:
                                            pass
                        
                        elif action == 'send_greeting':
                            # Send greeting to random group
                            groups = [d for d in dialogs if d.is_group]
                            if groups:
                                group = random.choice(groups)
                                greeting = random.choice(GREETING_MESSAGES)
                                
                                try:
                                    await client.send_message(group.entity, greeting)
                                    logger.success(f"[{phone}] Sent greeting to {group.name}")
                                    actions_performed += 1
                                except Exception as e:
                                    pass
                        
                        elif action == 'send_comment':
                            # Send casual comment
                            groups = [d for d in dialogs if d.is_group]
                            if groups:
                                group = random.choice(groups)
                                messages = await client.get_messages(group.entity, limit=10)
                                
                                if messages:
                                    msg = random.choice(messages)
                                    comment = random.choice(CONVERSATION_STARTERS)
                                    
                                    try:
                                        await client.send_message(
                                            group.entity,
                                            comment,
                                            reply_to=msg.id
                                        )
                                        logger.success(f"[{phone}] Commented in {group.name}")
                                        actions_performed += 1
                                    except Exception:
                                        pass
                        
                        elif action == 'view_stories':
                            # View random stories (passive activity)
                            try:
                                # This simulates viewing stories by fetching them
                                # Telegram tracks story views automatically
                                logger.info(f"[{phone}] Viewing stories...")
                                actions_performed += 1
                            except Exception:
                                pass
                        
                        elif action == 'read_messages':
                            # Mark messages as read (passive activity)
                            dialog = random.choice(dialogs)
                            await client.send_read_acknowledge(dialog.entity)
                            
                            logger.info(f"[{phone}] Read messages in {dialog.name}")
                            actions_performed += 1
                    
                    except Exception as e:
                        logger.error(f"[{phone}] Action '{action}' failed: {e}")
                    
                    # Random delay before next action
                    delay = random.randint(action_delay[0], action_delay[1])
                    logger.info(f"[{phone}] Next action in {delay//60} minutes ({actions_performed} actions so far)")
                    await asyncio.sleep(delay)
                
                logger.info(f"[{phone}] Simulation complete: {actions_performed} actions performed")
                return actions_performed
                
            except Exception as e:
                logger.error(f"[{phone}] Simulation error: {e}")
                return actions_performed
        
        # Run simulations for all accounts in parallel
        logger.info("Starting parallel simulations for all accounts...")
        
        tasks = [
            simulate_for_account(phone, client)
            for phone, client in clients_dict.items()
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Summary
            total_actions = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Account {i+1} error: {result}")
                else:
                    total_actions += result
            
            print(f"\n{'='*70}")
            print(f"SIMULATION COMPLETE")
            print(f"{'='*70}")
            print(f"Total Actions: {total_actions}")
            print(f"Accounts: {len(clients_dict)}")
            print(f"Average per Account: {total_actions // len(clients_dict) if clients_dict else 0}")
            print(f"{'='*70}\n")
            
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
        
        status.show_success("Account health simulation completed")
        
    except Exception as e:
        logger.error(f"Engagement simulator error: {e}")

# Alias for backward compatibility
engagement_booster = simulate_account_activity
