"""
Post Reactor Module
React to a specific post URL using all available accounts with mixed reactions.
"""

import asyncio
import random
from telethon import functions, types
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator

status = StatusIndicator()

# Verified positive reactions from auto_reactions.py
POSITIVE_REACTIONS = [
    '👍', '❤', '🔥', '🎉', '👏', '😁', '🤩', '💯'
]

async def react_to_post_with_all_accounts():
    """
    Feature 39: React to a specific post URL with all accounts using mixed positive reactions.
    """
    try:
        print(f"\n{'-'*70}")
        print("⭐ REACT TO POST WITH ALL ACCOUNTS")
        print(f"{'-'*70}\n")

        post_url = input("Enter the full post URL (e.g., https://t.me/channel/123): ").strip()
        if not post_url:
            status.show_error("Post URL cannot be empty.")
            return

        # Parse URL to get entity identifier and message ID
        entity_identifier = None
        msg_id = None

        if "t.me/c/" in post_url:
            # Private channel/group link: t.me/c/channel_id/msg_id
            try:
                parts = post_url.split("t.me/c/")[1].split("/")
                channel_id = int(parts[0])
                msg_id = int(parts[1])
                entity_identifier = int(f"-100{channel_id}")
            except (IndexError, ValueError):
                status.show_error("Invalid private link format. Should be: https://t.me/c/123456789/123")
                return
        elif "t.me/" in post_url:
            # Public link: t.me/username/msg_id
            try:
                parts = post_url.split("t.me/")[1].split("/")
                if len(parts) < 2:
                    status.show_error("Invalid public link format. Should be: https://t.me/username/123")
                    return
                username = parts[0]
                msg_id = int(parts[1])
                entity_identifier = username
            except (IndexError, ValueError):
                status.show_error("Invalid public link format. Should be: https://t.me/username/123")
                return
        else:
            status.show_error("Invalid URL format. Please provide a valid Telegram post URL.")
            return

        clients_dict = await session_manager.get_all_clients()
        if not clients_dict:
            status.show_error("No active accounts found. Please log in first.")
            return

        logger.info(f"Starting reactions on {post_url} with {len(clients_dict)} accounts.")
        logger.info(f"Using mixed reactions: {' '.join(POSITIVE_REACTIONS)}")

        success_count = 0
        
        async def react_with_account(phone, client):
            nonlocal success_count
            try:
                # User requested simultaneous/fast reactions for Option 39
                # Using minimal delay just to ensure order/stability
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
                if not client.is_connected(): await client.connect()
                entity = await client.get_entity(entity_identifier)
                reaction_emoji = random.choice(POSITIVE_REACTIONS)
                await client(functions.messages.SendReactionRequest(peer=entity, msg_id=msg_id, reaction=[types.ReactionEmoji(emoticon=reaction_emoji)]))
                logger.success(f"[{phone}] Reacted with {reaction_emoji} (Delay: {delay:.1f}s)")
                success_count += 1
            except Exception as e:
                logger.error(f"[{phone}] Failed to react: {e}")

        tasks = [react_with_account(phone, client) for phone, client in clients_dict.items()]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        status.show_success(f"Reaction process completed. Successful reactions: {success_count}/{len(clients_dict)}")

    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.warning("Reaction process cancelled by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the reaction process: {e}")