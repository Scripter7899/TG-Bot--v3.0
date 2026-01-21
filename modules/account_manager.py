"""
Account Management Module for FULL-TG v3.0
Features 1-10: Account operations
"""

import asyncio
from pathlib import Path
from datetime import datetime
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest, GetPasswordRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.auth import LogOutRequest
from telethon.errors import UsernameOccupiedError, UsernameInvalidError
from PIL import Image
import config
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator

status = StatusIndicator()

async def login_new_account():
    """Feature 1: Login new account"""
    try:
        phone = input("Enter phone number (with country code, e.g., +1234567890): ").strip()
        
        if not phone.startswith('+'):
            logger.error("Phone number must start with +")
            return
        
        status.show_processing(f"Logging in {phone}")
        client = await session_manager.login_account(phone)
        
        if client:
            status.show_success(f"Successfully logged in: {phone}")
        else:
            status.show_error("Login failed")
            
    except Exception as e:
        logger.error(f"Login error: {e}")

async def logout_account():
    """Feature 10: Logout Account (Delete Session)"""
    try:
        phone = input("Enter phone number to logout: ").strip()
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return

        confirm = input(f"Are you sure you want to logout {phone}? This will remove the session. (yes/no): ").strip().lower()
        if confirm == 'yes':
            # Use delete_session logic which handles cleanup
            result = await session_manager.delete_session(phone)
            if result:
                status.show_success(f"Logged out {phone}")
            else:
                status.show_error("Logout failed")
    except Exception as e:
        logger.error(f"Logout error: {e}")

async def get_account_info():
    """Feature 2: Get account info"""
    try:
        phone = input("Enter phone number: ").strip()
        
        status.show_processing("Fetching account info")
        info = await session_manager.get_account_info(phone)
        
        if info:
            print(f"\n{'-'*50}")
            print(f"Account Information:")
            print(f"{'-'*50}")
            print(f"ID: {info['id']}")
            print(f"Name: {info['first_name']} {info['last_name'] or ''}")
            print(f"Username: @{info['username']}" if info['username'] else "Username: Not set")
            print(f"Phone: {info['phone']}")
            print(f"Bio: {info['bio']}" if info['bio'] else "Bio: Not set")
            print(f"Premium: {'Yes' if info['premium'] else 'No'}")
            print(f"Verified: {'Yes' if info['verified'] else 'No'}")
            print(f"{'-'*50}\n")
            status.show_success("Account info retrieved")
        else:
            status.show_error("Failed to get account info")
            
    except Exception as e:
        logger.error(f"Error getting account info: {e}")

async def change_profile_name():
    """Feature 3: Change profile name"""
    try:
        print("\nOptions:")
        print("1. Change for specific account")
        print("2. Change for ALL accounts (Same Name)")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        if choice == '1':
            phone = input("Enter phone number: ").strip()
            client = await session_manager.get_client(phone)
            if not client: return
            
            first_name = input("Enter new first name: ").strip()
            last_name = input("Enter new last name (optional): ").strip()
            
            await client(UpdateProfileRequest(first_name=first_name, last_name=last_name or ''))
            status.show_success(f"Profile name updated for {phone}")
            
        elif choice == '2':
            first_name = input("Enter new first name for ALL: ").strip()
            last_name = input("Enter new last name for ALL (optional): ").strip()
            
            accounts = await db.get_all_accounts()
            print(f"\nUpdating {len(accounts)} accounts...")
            
            for account in accounts:
                phone = account[1]
                try:
                    client = await session_manager.get_client(phone)
                    if client:
                        if not client.is_connected(): await client.connect()
                        await client(UpdateProfileRequest(first_name=first_name, last_name=last_name or ''))
                        logger.success(f"Updated name for {phone}")
                        await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Failed to update {phone}: {e}")
            
            status.show_success("Bulk profile name update completed")
        
    except Exception as e:
        logger.error(f"Error changing profile name: {e}")

async def update_profile_picture():
    """Feature 4: Update profile picture"""
    try:
        print("\nOptions:")
        print("1. Update for specific account")
        print("2. Update for ALL accounts (Same Photo)")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        photo_path = input("Enter path to photo: ").strip()
        if not Path(photo_path).exists():
            status.show_error("Photo file not found")
            return
            
        if choice == '1':
            phone = input("Enter phone number: ").strip()
            client = await session_manager.get_client(phone)
            if not client: return
            
            status.show_processing("Uploading profile picture")
            file = await client.upload_file(photo_path)
            await client(UploadProfilePhotoRequest(file))
            status.show_success("Profile picture updated")
            
        elif choice == '2':
            accounts = await db.get_all_accounts()
            print(f"\nUpdating {len(accounts)} accounts...")
            
            for account in accounts:
                phone = account[1]
                try:
                    client = await session_manager.get_client(phone)
                    if client:
                        if not client.is_connected(): await client.connect()
                        file = await client.upload_file(photo_path)
                        await client(UploadProfilePhotoRequest(file))
                        logger.success(f"Updated photo for {phone}")
                        await asyncio.sleep(5) # Higher delay for media uploads
                except Exception as e:
                    logger.error(f"Failed to update {phone}: {e}")
        
    except Exception as e:
        logger.error(f"Error updating profile picture: {e}")

async def set_bio_status():
    """Feature 5: Set bio/status"""
    try:
        print("\nOptions:")
        print("1. Set for specific account")
        print("2. Set for ALL accounts (Same Bio)")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        if choice == '1':
            phone = input("Enter phone number: ").strip()
            client = await session_manager.get_client(phone)
            if not client: return
            
            bio = input("Enter new bio/about: ").strip()
            await client(UpdateProfileRequest(about=bio))
            status.show_success("Bio updated successfully")
            
        elif choice == '2':
            bio = input("Enter new bio for ALL: ").strip()
            accounts = await db.get_all_accounts()
            print(f"\nUpdating {len(accounts)} accounts...")
            
            for account in accounts:
                phone = account[1]
                try:
                    client = await session_manager.get_client(phone)
                    if client:
                        if not client.is_connected(): await client.connect()
                        await client(UpdateProfileRequest(about=bio))
                        logger.success(f"Updated bio for {phone}")
                        await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Failed to update {phone}: {e}")
        
    except Exception as e:
        logger.error(f"Error setting bio: {e}")

async def set_username():
    """Feature 6: Set username"""
    try:
        print("\nOptions:")
        print("1. Set for specific account")
        print("2. Set for ALL accounts (From File)")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        if choice == '1':
            phone = input("Enter phone number: ").strip()
            client = await session_manager.get_client(phone)
            if not client: return
            
            username = input("Enter new username (without @): ").strip()
            try:
                await client(UpdateUsernameRequest(username))
                status.show_success(f"Username set to @{username}")
            except UsernameOccupiedError:
                status.show_error("Username already taken")
            except UsernameInvalidError:
                status.show_error("Invalid username")
                
        elif choice == '2':
            file_path = input("Enter path to file (format: phone,username): ").strip()
            if not Path(file_path).exists():
                status.show_error("File not found")
                return
                
            print("\nProcessing bulk username update...")
            with open(file_path, 'r') as f:
                for line in f:
                    if ',' in line:
                        phone, username = line.strip().split(',', 1)
                        try:
                            client = await session_manager.get_client(phone.strip())
                            if client:
                                if not client.is_connected(): await client.connect()
                                await client(UpdateUsernameRequest(username.strip()))
                                logger.success(f"Set @{username} for {phone}")
                                await asyncio.sleep(5) # High delay for username changes
                        except Exception as e:
                            logger.error(f"Failed to set username for {phone}: {e}")
            
    except Exception as e:
        logger.error(f"Error setting username: {e}")

async def view_2fa_status():
    """Feature 7: View 2FA status"""
    try:
        print("\nOptions:")
        print("1. Check specific account")
        print("2. Check ALL accounts")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        async def check_2fa(phone, client):
            try:
                if not client.is_connected(): await client.connect()
                password = await client(GetPasswordRequest())
                status_text = "ENABLED" if password.has_password else "DISABLED"
                print(f"{phone}: {status_text}")
            except Exception as e:
                logger.error(f"Error checking {phone}: {e}")

        if choice == '1':
            phone = input("Enter phone number: ").strip()
            client = await session_manager.get_client(phone)
            if client:
                await check_2fa(phone, client)
                
        elif choice == '2':
            accounts = await db.get_all_accounts()
            print(f"\nChecking 2FA status for {len(accounts)} accounts...\n")
            
            for account in accounts:
                phone = account[1]
                client = await session_manager.get_client(phone)
                if client:
                    await check_2fa(phone, client)
            
    except Exception as e:
        logger.error(f"Error checking 2FA status: {e}")

async def terminate_other_sessions():
    """Feature 8: Terminate other sessions"""
    try:
        print("\nOptions:")
        print("1. Terminate for specific account")
        print("2. Terminate for ALL accounts (Security Sweep)")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        from telethon.tl.functions.auth import ResetAuthorizationsRequest
        
        if choice == '1':
            phone = input("Enter phone number: ").strip()
            client = await session_manager.get_client(phone)
            if not client: return
            
            if input("Confirm terminate other sessions? (yes/no): ").lower() == 'yes':
                await client(ResetAuthorizationsRequest())
                status.show_success("Other sessions terminated")
                
        elif choice == '2':
            if input("Confirm terminate other sessions for ALL accounts? (yes/no): ").lower() == 'yes':
                accounts = await db.get_all_accounts()
                print(f"\nSecuring {len(accounts)} accounts...")
                
                for account in accounts:
                    phone = account[1]
                    try:
                        client = await session_manager.get_client(phone)
                        if client:
                            if not client.is_connected(): await client.connect()
                            await client(ResetAuthorizationsRequest())
                            logger.success(f"Secured {phone}")
                    except Exception as e:
                        logger.error(f"Failed to secure {phone}: {e}")
        
    except Exception as e:
        logger.error(f"Error terminating sessions: {e}")

async def view_active_sessions():
    """Feature 9: View active sessions"""
    try:
        phone = input("Enter phone number: ").strip()
        client = await session_manager.get_client(phone)
        
        if not client:
            status.show_error("Account not found. Please login first.")
            return
        
        status.show_processing("Fetching active sessions")
        
        from telethon.tl.functions.account import GetAuthorizationsRequest
        authorizations = await client(GetAuthorizationsRequest())
        
        print(f"\n{'-'*70}")
        print(f"Active Sessions ({len(authorizations.authorizations)}):")
        print(f"{'-'*70}")
        
        for i, auth in enumerate(authorizations.authorizations, 1):
            print(f"\n{i}. Device: {auth.device_model}")
            print(f"   Platform: {auth.platform}")
            print(f"   Location: {auth.country}")
            print(f"   IP: {auth.ip}")
            print(f"   Active: {auth.date_active}")
            print(f"   Current: {'Yes' if auth.current else 'No'}")
        
        print(f"\n{'-'*70}\n")
        
    except Exception as e:
        logger.error(f"Error viewing sessions: {e}")

async def get_contact_list():
    """Feature 10: Get contact list"""
    try:
        phone = input("Enter phone number: ").strip()
        client = await session_manager.get_client(phone)
        
        if not client:
            status.show_error("Account not found. Please login first.")
            return
        
        status.show_processing("Fetching contacts")
        
        from telethon.tl.functions.contacts import GetContactsRequest
        contacts = await client(GetContactsRequest(hash=0))
        
        print(f"\n{'-'*70}")
        print(f"Contacts ({len(contacts.users)}):")
        print(f"{'-'*70}")
        
        for i, user in enumerate(contacts.users, 1):
            username = f"@{user.username}" if user.username else "No username"
            name = f"{user.first_name} {user.last_name or ''}".strip()
            print(f"{i}. {name} ({username}) - ID: {user.id}")
        
        print(f"\n{'-'*70}\n")
        
        # Export option
        export = input("Export to file? (yes/no): ").strip().lower()
        if export == 'yes':
            from datetime import datetime
            filename = config.EXPORTS_DIR / f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                for user in contacts.users:
                    username = f"@{user.username}" if user.username else "No username"
                    name = f"{user.first_name} {user.last_name or ''}".strip()
                    f.write(f"{name},{username},{user.id},{user.phone or 'N/A'}\n")
            
            status.show_success(f"Contacts exported to {filename}")
        
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
