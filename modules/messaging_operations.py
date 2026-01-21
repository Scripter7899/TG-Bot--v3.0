"""
Messaging Operations Module
Advanced messaging features
"""

import asyncio
from telethon.tl.functions.messages import SendMessageRequest, EditMessageRequest, DeleteMessagesRequest, ForwardMessagesRequest, UpdatePinnedMessageRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator
import config
from datetime import datetime

status = StatusIndicator()

async def send_message_to_group():
    """Feature 32: Send Message to Group"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        message = input("Enter message: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        await client.send_message(group, message)
        
        logger.success(f"Message sent to {group}")
        status.show_success("Message sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def send_media():
    """Feature 32: Send Media"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        file_path = input("Enter full path to file: ").strip()
        caption = input("Enter caption (optional): ").strip()
        
        if not asyncio.os.path.exists(file_path):
            status.show_error("File not found")
            return

        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        status.show_processing("Uploading media...")
        
        # Determine if force_document based on extension? 
        # For now, let telethon decide or default.
        await client.send_file(chat, file_path, caption=caption)
        
        logger.success(f"Media sent to {chat}")
        status.show_success("Media sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send media: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def send_reaction():
    """Feature 33: Send Reaction"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message_id = int(input("Enter message ID: ").strip())
        
        print("\nAvailable reactions: 👍 ❤️ 🔥 🎉 👏 😍 😮 😢")
        reaction = input("Enter reaction emoji: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        await client(SendReactionRequest(
            peer=entity,
            msg_id=message_id,
            reaction=[ReactionEmoji(emoticon=reaction)]
        ))
        
        logger.success(f"Reaction {reaction} sent to message {message_id}")
        status.show_success("Reaction sent")
        
    except Exception as e:
        logger.error(f"Failed to send reaction: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def pin_message():
    """Feature 34: Pin Message"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message_id = int(input("Enter message ID to pin: ").strip())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        await client(UpdatePinnedMessageRequest(
            peer=entity,
            id=message_id
        ))
        
        logger.success(f"Message {message_id} pinned")
        status.show_success("Message pinned")
        
    except Exception as e:
        logger.error(f"Failed to pin message: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def unpin_message():
    """Feature 35: Unpin Message"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        await client(UpdatePinnedMessageRequest(
            peer=entity,
            id=0,  # 0 means unpin
            unpin=True
        ))
        
        logger.success("Message unpinned")
        status.show_success("Message unpinned")
        
    except Exception as e:
        logger.error(f"Failed to unpin message: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def delete_messages():
    """Feature 37: Delete Messages"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message_ids = input("Enter message IDs (comma-separated): ").strip()
        
        ids = [int(x.strip()) for x in message_ids.split(',')]
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        await client.delete_messages(entity, ids)
        
        logger.success(f"Deleted {len(ids)} messages")
        status.show_success(f"Deleted {len(ids)} messages")
        
    except Exception as e:
        logger.error(f"Failed to delete messages: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def edit_message():
    """Feature 38: Edit Message"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message_id = int(input("Enter message ID to edit: ").strip())
        new_text = input("Enter new message text: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        await client.edit_message(entity, message_id, new_text)
        
        logger.success(f"Message {message_id} edited")
        status.show_success("Message edited")
        
    except Exception as e:
        logger.error(f"Failed to edit message: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def forward_messages():
    """Feature 39: Forward Messages"""
    try:
        phone = input("Enter your phone number: ").strip()
        from_chat = input("Enter source chat username: ").strip()
        to_chat = input("Enter destination chat username: ").strip()
        message_ids = input("Enter message IDs to forward (comma-separated): ").strip()
        
        ids = [int(x.strip()) for x in message_ids.split(',')]
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from_entity = await client.get_entity(from_chat)
        to_entity = await client.get_entity(to_chat)
        
        await client.forward_messages(to_entity, ids, from_entity)
        
        logger.success(f"Forwarded {len(ids)} messages")
        status.show_success(f"Forwarded {len(ids)} messages")
        
    except Exception as e:
        logger.error(f"Failed to forward messages: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def export_messages():
    """Feature 40: Export Messages"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        limit = int(input("How many messages to export? (0 for all): ").strip())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        messages = []
        
        status.show_processing("Exporting messages...")
        
        async for message in client.iter_messages(entity, limit=limit if limit > 0 else None):
            messages.append({
                'id': message.id,
                'date': str(message.date),
                'sender_id': message.sender_id,
                'text': message.text or '',
                'media': 'Yes' if message.media else 'No'
            })
        
        # Export to file
        filename = config.EXPORTS_DIR / f"messages_{entity.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        config.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            for msg in messages:
                f.write(f"[{msg['date']}] ID:{msg['id']} Sender:{msg['sender_id']}\n")
                f.write(f"{msg['text']}\n")
                f.write(f"Media: {msg['media']}\n")
                f.write(f"{'-'*70}\n")
        
        logger.success(f"Exported {len(messages)} messages to {filename}")
        status.show_success(f"Exported {len(messages)} messages")
        
    except Exception as e:
        logger.error(f"Failed to export messages: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def search_messages():
    """Feature 36: Search Messages"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        query = input("Enter search query: ").strip()
        limit = int(input("Max results (default 100): ").strip() or "100")
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        
        print(f"\n{'='*70}")
        print(f"SEARCH RESULTS: '{query}'")
        print(f"{'='*70}\n")
        
        found = 0
        async for message in client.iter_messages(entity, limit=limit, search=query):
            print(f"[{message.date}] ID: {message.id}")
            print(f"From: {message.sender_id}")
            print(f"Text: {message.text[:100] if message.text else 'No text'}")
            print(f"{'-'*70}")
            found += 1
        
        print(f"\nFound {found} messages\n")
        status.show_success(f"Found {found} messages")
        
    except Exception as e:
        logger.error(f"Failed to search messages: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_message_info():
    """Feature 40: Get Message Info"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message_id = int(input("Enter message ID: ").strip())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        message = await client.get_messages(entity, ids=message_id)
        
        if not message:
            status.show_error("Message not found or inaccessible")
            return

        print(f"\n{'='*70}")
        print(f"MESSAGE INFO (ID: {message.id})")
        print(f"{'='*70}")
        print(f"Date: {message.date}")
        print(f"Edit Date: {message.edit_date if message.edit_date else 'Never'}")
        print(f"Sender ID: {message.sender_id}")
        print(f"Group ID: {entity.id}")
        
        # Content Info
        print(f"{'-'*30}")
        print(f"Text Content: {message.text[:100] + '...' if message.text and len(message.text) > 100 else message.text or 'No Text'}")
        
        # Media Info
        media_type = "None"
        if message.photo: media_type = "Photo"
        elif message.video: media_type = "Video"
        elif message.document: media_type = "Document"
        elif message.voice: media_type = "Voice/Audio"
        elif message.sticker: media_type = "Sticker"
        
        print(f"Media: {media_type}")
        if message.file:
            print(f"File Name: {message.file.name if hasattr(message.file, 'name') else 'N/A'}")
            print(f"Size: {message.file.size} bytes")
            print(f"Mime: {message.file.mime_type}")

        # Forward Info
        if message.fwd_from:
            print(f"{'-'*30}")
            print(f"Forwarded From: {message.fwd_from.from_id or message.fwd_from.from_name}")
            print(f"Original Date: {message.fwd_from.date}")

        # Reply Info
        if message.reply_to:
            print(f"Reply To ID: {message.reply_to.reply_to_msg_id}")

        print(f"{'='*70}\n")
        
        status.show_success("Message info retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get message info: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def view_message_stats():
    """Feature 41: View Message Stats"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message_id = int(input("Enter message ID: ").strip())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        message = await client.get_messages(entity, ids=message_id)
        
        print(f"\n{'='*70}")
        print(f"MESSAGE STATS")
        print(f"{'='*70}")
        print(f"Message ID: {message.id}")
        print(f"Date: {message.date}")
        print(f"Sender: {message.sender_id}")
        print(f"Views: {message.views if hasattr(message, 'views') else 'N/A'}")
        print(f"Forwards: {message.forwards if hasattr(message, 'forwards') else 'N/A'}")
        print(f"Replies: {message.replies.replies if hasattr(message, 'replies') and message.replies else 0}")
        print(f"Reactions: {len(message.reactions.results) if hasattr(message, 'reactions') and message.reactions else 0}")
        print(f"{'='*70}\n")
        
        status.show_success("Message stats retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get message stats: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_message_link():
    """Feature 42: Get Message Link"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message_id = int(input("Enter message ID: ").strip())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        
        # Generate message link
        if hasattr(entity, 'username') and entity.username:
            link = f"https://t.me/{entity.username}/{message_id}"
        else:
            link = f"https://t.me/c/{str(entity.id)[4:]}/{message_id}"
        
        print(f"\n{'='*70}")
        print(f"MESSAGE LINK")
        print(f"{'='*70}")
        print(f"Link: {link}")
        print(f"{'='*70}\n")
        
        logger.success(f"Message link: {link}")
        status.show_success("Message link generated")
        
    except Exception as e:
        logger.error(f"Failed to get message link: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def message_analytics():
    """Feature 45: Message Analytics"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        limit = int(input("Analyze last N messages (default 100): ").strip() or "100")
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        
        status.show_processing("Analyzing messages...")
        
        total_messages = 0
        total_views = 0
        total_forwards = 0
        media_count = 0
        
        async for message in client.iter_messages(entity, limit=limit):
            total_messages += 1
            if hasattr(message, 'views') and message.views:
                total_views += message.views
            if hasattr(message, 'forwards') and message.forwards:
                total_forwards += message.forwards
            if message.media:
                media_count += 1
        
        print(f"\n{'='*70}")
        print(f"MESSAGE ANALYTICS")
        print(f"{'='*70}")
        print(f"Total Messages Analyzed: {total_messages}")
        print(f"Total Views: {total_views}")
        print(f"Total Forwards: {total_forwards}")
        print(f"Messages with Media: {media_count}")
        print(f"Avg Views per Message: {total_views // total_messages if total_messages > 0 else 0}")
        print(f"Media Percentage: {(media_count / total_messages * 100):.1f}%" if total_messages > 0 else "0%")
        print(f"{'='*70}\n")
        
        status.show_success("Analytics complete")
        
    except Exception as e:
        logger.error(f"Failed to analyze messages: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def schedule_message():
    """Feature 43: Schedule Message"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message = input("Enter message: ").strip()
        
        print("\nSchedule for:")
        print("1. 1 hour from now")
        print("2. 6 hours from now")
        print("3. 24 hours from now")
        print("4. Custom time")
        choice = input("Select option (1-4): ").strip()
        
        from datetime import datetime, timedelta
        
        if choice == '1':
            schedule_time = datetime.now() + timedelta(hours=1)
        elif choice == '2':
            schedule_time = datetime.now() + timedelta(hours=6)
        elif choice == '3':
            schedule_time = datetime.now() + timedelta(hours=24)
        elif choice == '4':
            hours = int(input("Hours from now: ").strip())
            schedule_time = datetime.now() + timedelta(hours=hours)
        else:
            print("Invalid choice")
            return
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        
        # Schedule message
        await client.send_message(entity, message, schedule=schedule_time)
        
        print(f"\nMessage scheduled for: {schedule_time}")
        logger.success(f"Message scheduled for {schedule_time}")
        status.show_success("Message scheduled")
        
    except Exception as e:
        logger.error(f"Failed to schedule message: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def bulk_delete():
    """Feature 44: Bulk Delete"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        
        print("\nDelete options:")
        print("1. Delete last N messages")
        print("2. Delete all messages")
        print("3. Delete messages from date range")
        choice = input("Select option (1-3): ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        
        if choice == '1':
            limit = int(input("How many messages to delete: ").strip())
            confirm = input(f"Delete last {limit} messages? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                message_ids = []
                async for message in client.iter_messages(entity, limit=limit):
                    message_ids.append(message.id)
                
                await client.delete_messages(entity, message_ids)
                print(f"\nDeleted {len(message_ids)} messages")
                logger.success(f"Bulk deleted {len(message_ids)} messages")
                status.show_success(f"Deleted {len(message_ids)} messages")
        
        elif choice == '2':
            confirm = input("Delete ALL messages? This cannot be undone! (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                deleted = 0
                batch = []
                async for message in client.iter_messages(entity):
                    batch.append(message.id)
                    if len(batch) >= 100:
                        try:
                            await client.delete_messages(entity, batch)
                            deleted += len(batch)
                            batch = []
                            print(f"Deleted {deleted} messages...")
                            await asyncio.sleep(1) # Safety delay between batches
                        except Exception as e:
                            logger.error(f"Failed to delete batch: {e}")
                
                # Delete remaining
                if batch:
                    try:
                        await client.delete_messages(entity, batch)
                        deleted += len(batch)
                    except Exception as e:
                        logger.error(f"Failed to delete remaining: {e}")
                
                print(f"\nDeleted {deleted} messages total")
                logger.success(f"Bulk deleted {deleted} messages")
                status.show_success(f"Deleted {deleted} messages")
        
        elif choice == '3':
            print("Date range deletion not implemented")
        
    except Exception as e:
        logger.error(f"Failed bulk delete: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")


