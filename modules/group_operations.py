"""
Group Operations Module
Advanced group management features
"""

import asyncio
from telethon.tl.functions.channels import GetFullChannelRequest, EditBannedRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest, ExportChatInviteRequest
from telethon.tl.types import ChatBannedRights
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator
from datetime import datetime, timedelta

status = StatusIndicator()

async def create_group():
    """Feature 46: Create Group"""
    try:
        phone = input("Enter your phone number: ").strip()
        title = input("Enter new group title: ").strip()
        desc = input("Enter group description (optional): ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
            
        from telethon.tl.functions.channels import CreateChannelRequest, EditChatAboutRequest
        
        status.show_processing("Creating group...")
        
        # Create user assumes megagroup usually
        result = await client(CreateChannelRequest(
            title=title,
            about=desc,
            megagroup=True
        ))
        
        # New Chat ID
        new_chat = result.chats[0]
        
        logger.success(f"Created group '{title}' (ID: {new_chat.id})")
        status.show_success(f"Group created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create group: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def add_members():
    """Feature 48: Add Members"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        users_input = input("Enter usernames/phones to add (comma separated): ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
            
        from telethon.tl.functions.channels import InviteToChannelRequest
        
        targets = [x.strip() for x in users_input.split(',') if x.strip()]
        if not targets:
            return

        status.show_processing(f"Adding {len(targets)} members...")
        
        entity = await client.get_entity(group)
        
        # Add in batches if needed, but simple for now
        # Telethon accepts list of users
        await client(InviteToChannelRequest(
            channel=entity,
            users=targets
        ))
        
        logger.success(f"Added members to {group}")
        status.show_success("Members added successfully")
        
    except Exception as e:
        logger.error(f"Failed to add members: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_members_count():
    """Feature 48: Get Members Count"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(group)
        full = await client(GetFullChannelRequest(channel=entity))
        
        print(f"\n{'='*70}")
        print(f"MEMBERS COUNT: {entity.title}")
        print(f"{'='*70}")
        print(f"Total Members: {full.full_chat.participants_count}")
        print(f"Online: {full.full_chat.online_count if hasattr(full.full_chat, 'online_count') else 'N/A'}")
        print(f"{'='*70}\n")
        
        status.show_success("Members count retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get members count: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_group_link():
    """Feature 50: Get Group Link"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(group)
        
        # Get invite link
        invite = await client(ExportChatInviteRequest(peer=entity))
        
        print(f"\n{'='*70}")
        print(f"GROUP INVITE LINK")
        print(f"{'='*70}")
        print(f"Group: {entity.title}")
        print(f"Link: {invite.link}")
        print(f"{'='*70}\n")
        
        logger.success(f"Invite link: {invite.link}")
        status.show_success("Invite link retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get group link: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def mute_user():
    """Feature 54: Mute User"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        user_to_mute = input("Enter username to mute: ").strip()
        duration = int(input("Mute duration in minutes (0 for forever): ").strip())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        group_entity = await client.get_entity(group)
        user_entity = await client.get_entity(user_to_mute)
        
        # Calculate until_date
        if duration == 0:
            until_date = None  # Forever
        else:
            until_date = datetime.now() + timedelta(minutes=duration)
        
        # Mute user (restrict sending messages)
        await client(EditBannedRequest(
            channel=group_entity,
            participant=user_entity,
            banned_rights=ChatBannedRights(
                until_date=until_date,
                send_messages=True
            )
        ))
        
        logger.success(f"Muted {user_to_mute} in {group}")
        status.show_success(f"User muted for {duration} minutes" if duration > 0 else "User muted forever")
        
    except Exception as e:
        logger.error(f"Failed to mute user: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def kick_user():
    """Feature 56: Kick User"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        user_to_kick = input("Enter username to kick: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        group_entity = await client.get_entity(group)
        user_entity = await client.get_entity(user_to_kick)
        
        # Kick user (ban and then unban to remove from group)
        await client.kick_participant(group_entity, user_entity)
        
        logger.success(f"Kicked {user_to_kick} from {group}")
        status.show_success("User kicked from group")
        
    except Exception as e:
        logger.error(f"Failed to kick user: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def lock_group():
    """Feature 59: Lock Group"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        group_entity = await client.get_entity(group)
        
        # Lock group (restrict all members from sending messages)
        await client(EditChatDefaultBannedRightsRequest(
            peer=group_entity,
            banned_rights=ChatBannedRights(
                until_date=None,
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True
            )
        ))
        
        logger.success(f"Locked group: {group}")
        status.show_success("Group locked - members cannot send messages")
        
    except Exception as e:
        logger.error(f"Failed to lock group: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def group_statistics():
    """Feature 49: Group Statistics"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(group)
        full = await client(GetFullChannelRequest(channel=entity))
        
        # Get recent message stats
        messages_count = 0
        async for _ in client.iter_messages(entity, limit=100):
            messages_count += 1
        
        print(f"\n{'='*70}")
        print(f"GROUP STATISTICS: {entity.title}")
        print(f"{'='*70}")
        print(f"Total Members: {full.full_chat.participants_count}")
        print(f"Online Now: {full.full_chat.online_count if hasattr(full.full_chat, 'online_count') else 'N/A'}")
        print(f"Recent Messages (last 100): {messages_count}")
        print(f"Admins: {full.full_chat.admins_count if hasattr(full.full_chat, 'admins_count') else 'N/A'}")
        print(f"Banned: {full.full_chat.kicked_count if hasattr(full.full_chat, 'kicked_count') else 'N/A'}")
        print(f"{'='*70}\n")
        
        status.show_success("Statistics retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get group statistics: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def change_group_title():
    """Feature 51: Change Group Title"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        new_title = input("Enter new group title: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(group)
        await client.edit_folder(entity, title=new_title)
        
        logger.success(f"Changed group title to: {new_title}")
        status.show_success("Group title changed")
        
    except Exception as e:
        logger.error(f"Failed to change group title: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def change_group_description():
    """Feature 52: Change Group Description"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        new_description = input("Enter new description: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from telethon.tl.functions.messages import EditChatAboutRequest
        entity = await client.get_entity(group)
        await client(EditChatAboutRequest(peer=entity, about=new_description))
        
        logger.success("Group description changed")
        status.show_success("Description updated")
        
    except Exception as e:
        logger.error(f"Failed to change description: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def get_member_info():
    """Feature 53: Get Member Info"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        member_username = input("Enter member username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        group_entity = await client.get_entity(group)
        member = await client.get_entity(member_username)
        
        # Get participant info
        from telethon.tl.functions.channels import GetParticipantRequest
        participant = await client(GetParticipantRequest(
            channel=group_entity,
            participant=member
        ))
        
        print(f"\n{'='*70}")
        print(f"MEMBER INFO")
        print(f"{'='*70}")
        print(f"User ID: {member.id}")
        print(f"Username: @{member.username}" if member.username else "No username")
        print(f"Name: {member.first_name} {member.last_name or ''}")
        print(f"Status: {participant.participant.__class__.__name__}")
        print(f"{'='*70}\n")
        
        status.show_success("Member info retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get member info: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def unmute_user():
    """Feature 55: Unmute User"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        user_to_unmute = input("Enter username to unmute: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        group_entity = await client.get_entity(group)
        user_entity = await client.get_entity(user_to_unmute)
        
        # Unmute user (remove restrictions)
        await client(EditBannedRequest(
            channel=group_entity,
            participant=user_entity,
            banned_rights=ChatBannedRights(
                until_date=None,
                send_messages=False
            )
        ))
        
        logger.success(f"Unmuted {user_to_unmute}")
        status.show_success("User unmuted")
        
    except Exception as e:
        logger.error(f"Failed to unmute user: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def make_admin():
    """Feature 57: Make Admin"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        user_to_promote = input("Enter username to make admin: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from telethon.tl.functions.channels import EditAdminRequest
        from telethon.tl.types import ChatAdminRights
        
        group_entity = await client.get_entity(group)
        user_entity = await client.get_entity(user_to_promote)
        
        # Promote to admin with basic rights
        await client(EditAdminRequest(
            channel=group_entity,
            user_id=user_entity,
            admin_rights=ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=False
            ),
            rank='Admin'
        ))
        
        logger.success(f"Made {user_to_promote} an admin")
        status.show_success("User promoted to admin")
        
    except Exception as e:
        logger.error(f"Failed to make admin: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def remove_admin():
    """Feature 58: Remove Admin"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        user_to_demote = input("Enter username to remove admin: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from telethon.tl.functions.channels import EditAdminRequest
        from telethon.tl.types import ChatAdminRights
        
        group_entity = await client.get_entity(group)
        user_entity = await client.get_entity(user_to_demote)
        
        # Remove admin rights
        await client(EditAdminRequest(
            channel=group_entity,
            user_id=user_entity,
            admin_rights=ChatAdminRights(),
            rank=''
        ))
        
        logger.success(f"Removed admin rights from {user_to_demote}")
        status.show_success("Admin rights removed")
        
    except Exception as e:
        logger.error(f"Failed to remove admin: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def unlock_group():
    """Feature 60: Unlock Group"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        group_entity = await client.get_entity(group)
        
        # Unlock group (remove all restrictions)
        await client(EditChatDefaultBannedRightsRequest(
            peer=group_entity,
            banned_rights=ChatBannedRights(
                until_date=None,
                send_messages=False,
                send_media=False,
                send_stickers=False,
                send_gifs=False,
                send_games=False,
                send_inline=False,
                embed_links=False
            )
        ))
        
        logger.success(f"Unlocked group: {group}")
        status.show_success("Group unlocked - members can send messages")
        
    except Exception as e:
        logger.error(f"Failed to unlock group: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

