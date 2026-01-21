"""
Reporting Operations Module
Reporting and moderation features
"""

import asyncio
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.messages import ReportRequest, DeleteHistoryRequest
from telethon.tl.types import InputReportReasonSpam, InputReportReasonViolence, InputReportReasonPornography, InputReportReasonOther
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator

status = StatusIndicator()

async def report_group():
    """Feature 61: Report Group"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link to report: ").strip()
        
        print("\nReport Reasons:")
        print("1. Spam")
        print("2. Violence")
        print("3. Pornography")
        print("4. Other")
        reason_choice = input("Select reason (1-4): ").strip()
        
        reason_map = {
            '1': InputReportReasonSpam(),
            '2': InputReportReasonViolence(),
            '3': InputReportReasonPornography(),
            '4': InputReportReasonOther()
        }
        reason = reason_map.get(reason_choice, InputReportReasonSpam())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(group)
        await client(ReportPeerRequest(peer=entity, reason=reason, message=""))
        
        logger.success(f"Reported group: {group}")
        status.show_success("Group reported successfully")
        
    except Exception as e:
        logger.error(f"Failed to report group: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def report_message():
    """Feature 62: Report Message"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat/group username: ").strip()
        message_ids = input("Enter message IDs to report (comma-separated): ").strip()
        
        ids = [int(x.strip()) for x in message_ids.split(',')]
        
        print("\nReport Reasons:")
        print("1. Spam")
        print("2. Violence")
        print("3. Pornography")
        print("4. Other")
        reason_choice = input("Select reason (1-4): ").strip()
        
        reason_map = {
            '1': InputReportReasonSpam(),
            '2': InputReportReasonViolence(),
            '3': InputReportReasonPornography(),
            '4': InputReportReasonOther()
        }
        reason = reason_map.get(reason_choice, InputReportReasonSpam())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        await client(ReportRequest(peer=entity, id=ids, reason=reason, message=""))
        
        logger.success(f"Reported {len(ids)} messages")
        status.show_success(f"Reported {len(ids)} messages")
        
    except Exception as e:
        logger.error(f"Failed to report messages: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def clear_chat_history():
    """Feature 63: Clear Chat History"""
    try:
        phone = input("Enter your phone number: ").strip()
        chat = input("Enter chat username to clear: ").strip()
        
        confirm = input(f"Clear ALL history with {chat}? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(chat)
        await client(DeleteHistoryRequest(peer=entity, max_id=0, just_clear=True))
        
        logger.success(f"Cleared chat history with {chat}")
        status.show_success("Chat history cleared")
        
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def restrict_user():
    """Feature 64: Restrict User"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        user_to_restrict = input("Enter username to restrict: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from telethon.tl.functions.channels import EditBannedRequest
        from telethon.tl.types import ChatBannedRights
        
        group_entity = await client.get_entity(group)
        user_entity = await client.get_entity(user_to_restrict)
        
        # Restrict user (can't send media, stickers, etc.)
        await client(EditBannedRequest(
            channel=group_entity,
            participant=user_entity,
            banned_rights=ChatBannedRights(
                until_date=None,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True
            )
        ))
        
        logger.success(f"Restricted {user_to_restrict}")
        status.show_success("User restricted (can only send text)")
        
    except Exception as e:
        logger.error(f"Failed to restrict user: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def mute_user_forever():
    """Feature 65: Mute User Forever"""
    try:
        phone = input("Enter your phone number: ").strip()
        group = input("Enter group username/link: ").strip()
        user_to_mute = input("Enter username to mute forever: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from telethon.tl.functions.channels import EditBannedRequest
        from telethon.tl.types import ChatBannedRights
        
        group_entity = await client.get_entity(group)
        user_entity = await client.get_entity(user_to_mute)
        
        # Mute forever
        await client(EditBannedRequest(
            channel=group_entity,
            participant=user_entity,
            banned_rights=ChatBannedRights(
                until_date=None,
                send_messages=True
            )
        ))
        
        logger.success(f"Muted {user_to_mute} forever")
        status.show_success("User muted permanently")
        
    except Exception as e:
        logger.error(f"Failed to mute user: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def spam_report():
    """Feature 66: Spam Report"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter username/group to report as spam: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(target)
        await client(ReportPeerRequest(peer=entity, reason=InputReportReasonSpam(), message="Spam"))
        
        logger.success(f"Reported {target} as spam")
        status.show_success("Spam report submitted")
        
    except Exception as e:
        logger.error(f"Failed to report spam: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def content_report():
    """Feature 67: Content Report"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter username/group to report: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(target)
        await client(ReportPeerRequest(peer=entity, reason=InputReportReasonOther(), message="Inappropriate content"))
        
        logger.success(f"Reported {target} for inappropriate content")
        status.show_success("Content report submitted")
        
    except Exception as e:
        logger.error(f"Failed to report content: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def bot_report():
    """Feature 68: Bot Report"""
    try:
        phone = input("Enter your phone number: ").strip()
        bot_username = input("Enter bot username to report: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(bot_username)
        await client(ReportPeerRequest(peer=entity, reason=InputReportReasonSpam(), message="Malicious bot"))
        
        logger.success(f"Reported bot: {bot_username}")
        status.show_success("Bot reported")
        
    except Exception as e:
        logger.error(f"Failed to report bot: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def advanced_report():
    """Feature 70: Advanced Report"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter target to report: ").strip()
        
        print("\nReport Types:")
        print("1. Spam")
        print("2. Violence")
        print("3. Pornography")
        print("4. Child Abuse")
        print("5. Copyright")
        print("6. Other")
        
        report_type = input("Select type (1-6): ").strip()
        custom_message = input("Enter custom report message: ").strip()
        
        reason_map = {
            '1': InputReportReasonSpam(),
            '2': InputReportReasonViolence(),
            '3': InputReportReasonPornography(),
            '4': InputReportReasonOther(),
            '5': InputReportReasonOther(),
            '6': InputReportReasonOther()
        }
        reason = reason_map.get(report_type, InputReportReasonOther())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(target)
        await client(ReportPeerRequest(peer=entity, reason=reason, message=custom_message))
        
        logger.success(f"Advanced report submitted for {target}")
        status.show_success("Report submitted successfully")
        
    except Exception as e:
        logger.error(f"Failed to submit report: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")
