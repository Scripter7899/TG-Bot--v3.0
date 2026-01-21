import asyncio
import random
from telethon import functions, types
from core.session_manager import session_manager
from core.logger import logger
from ui.colors import *
from ui.progress import StatusIndicator

status = StatusIndicator()

async def increase_view_count():
    """
    Feature 125: Increase View Count
    Uses all active accounts to view a specific post link.
    """
    print(f"\n{'-'*60}")
    print(f"{BOLD}👁️  INCREASE VIEW COUNT [ALL ACCOUNTS]{RESET}")
    print(f"{'-'*60}\n")
    
    # Get inputs
    post_link = input(f"{PROMPT}Enter post link (e.g., https://t.me/channel/123): {RESET}").strip()
    
    if not post_link:
        status.show_error("Invalid link")
        return

    # Parse link
    try:
        if "t.me/c/" in post_link:
            # Private link: https://t.me/c/1234567890/123
            parts = post_link.split('/')
            channel_id = int(parts[-2])
            msg_id = int(parts[-1])
            # For private channels, we might need -100 prefix if not present
            # But t.me/c/ usually has the ID without -100, but telethon expects peer
            # We'll try resolving it. Usually need to be a member.
        else:
            # Public link: https://t.me/channelname/123
            parts = post_link.split('/')
            channel_username = parts[-2]
            msg_id = int(parts[-1])
    except Exception:
        status.show_error("Invalid link format. Use https://t.me/channel/123")
        return

    # Get accounts
    clients = await session_manager.get_all_clients()
    if not clients:
        status.show_error("No active sessions found")
        return
    
    print(f"\n{INFO}Loaded {len(clients)} accounts. Starting view operation...{RESET}")
    print(f"{INFO}Delay between views: 2-15 seconds (Randomized){RESET}\n")
    
    success_count = 0
    fail_count = 0
    
    for i, (phone, client) in enumerate(clients.items(), 1):
        try:
            print(f"[{i}/{len(clients)}] Processing {phone}...", end="\r")
            
            # Resolve entity
            entity = None
            if "t.me/c/" in post_link:
                # Private channel logic - simplified, assumes member or access
                # Try to resolve by ID if possible, mostly works if joined
                try:
                    # Append -100 if missing for private channel access via ID
                    # This is tricky without being member. 
                    # We will try to rely on client.get_messages accepting a joined channel input
                    pass 
                except Exception:
                    pass
            else:
                try:
                    entity = await client.get_entity(channel_username)
                except Exception:
                    # Maybe need to join?
                    try:
                        await client(functions.channels.JoinChannelRequest(channel_username))
                        entity = await client.get_entity(channel_username)
                    except Exception:
                        pass
            
            # Use the link directly if entity resolution is complex, 
            # get_messages often handles username/id if formatted right?
            # Actually get_messages needs an entity (chat).
            
            target = None
            if "t.me/c/" in post_link:
                # For private chats, we assume options:
                # 1. Account is already member -> can access by ID
                # 2. Account is NOT member -> Cannot view
                # We'll try to use the integer ID provided in link
                # Note: t.me/c/123456/123 -> Channel ID is -100123456 usually
                # Let's try constructing the peer
                try:
                    peer_id = int(f"-100{channel_id}")
                    target = peer_id
                except Exception:
                    target = channel_id
            else:
                target = channel_username

            # VIEW ACTION: Fetch message + Explicitly Increment View
            # 1. Get the message to ensure it exists
            msgs = await client.get_messages(target, ids=msg_id)
            
            if msgs:
                # 2. Key Step: Request View Increment
                # This is the specific API call Telegram clients use to say "I am looking at this"
                try:
                    await client(functions.messages.GetMessagesViewsRequest(
                        peer=target,
                        id=[msg_id],
                        increment=True
                    ))
                except Exception as e:
                    # Some entities might not support this or return generic errors, but we continue
                    # logger.debug(f"View increment error: {e}")
                    pass

                # 3. Mark as read (Doubletap)
                await client.send_read_acknowledge(target, msgs)

                success_count += 1
                # logger.success(f"[{phone}] Viewed message {msg_id}")
            else:
                fail_count += 1
                logger.warning(f"[{phone}] Message {msg_id} not found")
                pass
            
            # Human Delay
            delay = random.uniform(2, 8)
            await asyncio.sleep(delay)
            
        except Exception as e:
            fail_count += 1
            logger.error(f"[{phone}] Failed: {e}")
            
    print(f"\n{SUCCESS}Operation Complete!{RESET}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    
    input(f"\n{PROMPT}Press Enter to return...{RESET}")
