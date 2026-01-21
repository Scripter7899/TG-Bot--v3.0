"""
User Operations Module
Additional user-related features
"""

import asyncio
from telethon.tl.functions.contacts import AddContactRequest, BlockRequest, UnblockRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetChannelsRequest
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator

status = StatusIndicator()

async def add_contact():
    """Feature 23: Add Contact"""
    try:
        phone = input("Enter your phone number: ").strip()
        target_username = input("Enter target username (without @): ").strip()
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name (optional): ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        user = await client.get_entity(target_username)
        await client(AddContactRequest(
            id=user.id,
            first_name=first_name,
            last_name=last_name or '',
            phone=user.phone or ''
        ))
        
        logger.success(f"Added {target_username} to contacts")
        status.show_success(f"Contact added: {first_name}")
        
    except Exception as e:
        logger.error(f"Failed to add contact: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def block_user():
    """Feature 24: Block User"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter username/phone to block: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        user = await client.get_entity(target)
        await client(BlockRequest(id=user.id))
        
        logger.success(f"Blocked {target}")
        status.show_success(f"User blocked")
        
    except Exception as e:
        logger.error(f"Failed to block user: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def unblock_user():
    """Feature 25: Unblock User"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter username/phone to unblock: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        user = await client.get_entity(target)
        await client(UnblockRequest(id=user.id))
        
        logger.success(f"Unblocked {target}")
        status.show_success(f"User unblocked")
        
    except Exception as e:
        logger.error(f"Failed to unblock user: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def find_user():
    """Feature 26: Find User"""
    try:
        phone = input("Enter your phone number: ").strip()
        search_query = input("Enter search query (username/name): ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        # Search in contacts
        result = await client.get_contacts()
        
        print(f"\n{'='*70}")
        print(f"SEARCH RESULTS FOR: {search_query}")
        print(f"{'='*70}\n")
        
        found = 0
        for user in result:
            if search_query.lower() in (user.first_name or '').lower() or \
               search_query.lower() in (user.last_name or '').lower() or \
               search_query.lower() in (user.username or '').lower():
                print(f"ID: {user.id}")
                print(f"Name: {user.first_name} {user.last_name or ''}")
                print(f"Username: @{user.username}" if user.username else "No username")
                print(f"{'-'*70}")
                found += 1
        
        print(f"\nFound {found} users\n")
        
    except Exception as e:
        logger.error(f"Failed to search: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_mutual_friends():
    """Feature 27: Get Mutual Friends"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter target username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        user = await client.get_entity(target)
        full_user = await client(GetFullUserRequest(id=user.id))
        
        print(f"\n{'='*70}")
        print(f"MUTUAL CONTACTS WITH: @{target}")
        print(f"{'='*70}")
        print(f"Common Groups: {full_user.full_user.common_chats_count}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Failed to get mutual friends: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_last_seen():
    """Feature 28: Get Last Seen"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter target username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        user = await client.get_entity(target)
        
        print(f"\n{'='*70}")
        print(f"LAST SEEN: @{target}")
        print(f"{'='*70}")
        
        if hasattr(user.status, 'was_online'):
            print(f"Last Seen: {user.status.was_online}")
        elif hasattr(user.status, '__class__'):
            print(f"Status: {user.status.__class__.__name__}")
        else:
            print("Status: Hidden")
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Failed to get last seen: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_user_channels():
    """Feature 30: Get User Channels"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter target username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        user = await client.get_entity(target)
        full_user = await client(GetFullUserRequest(id=user.id))
        
        print(f"\n{'='*70}")
        print(f"CHANNELS/GROUPS: @{target}")
        print(f"{'='*70}")
        print(f"Common Chats: {full_user.full_user.common_chats_count}")
        print(f"{'='*70}\n")
        
        status.show_success("Information retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get user channels: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_user_followers():
    """Feature 29: Get User Followers"""
    try:
        phone = input("Enter your phone number: ").strip()
        channel = input("Enter channel username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from telethon.tl.functions.channels import GetFullChannelRequest
        
        entity = await client.get_entity(channel)
        full = await client(GetFullChannelRequest(channel=entity))
        
        print(f"\n{'='*70}")
        print(f"FOLLOWERS: {entity.title}")
        print(f"{'='*70}")
        print(f"Total Subscribers: {full.full_chat.participants_count}")
        print(f"{'='*70}\n")
        
        status.show_success("Followers count retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get followers: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

