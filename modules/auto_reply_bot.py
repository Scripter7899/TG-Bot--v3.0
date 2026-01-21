"""
Auto-Reply Bot Module - FIXED
Multi-account auto-reply system with proper event handling
"""

import asyncio
import random
from telethon import events
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator

status = StatusIndicator()

# Response templates
RESPONSE_TEMPLATES = {
    'greeting': [
        "Hello! How can I help you?",
        "Hi there! What can I do for you?",
        "Hey! How may I assist you?"
    ],
    'thanks': [
        "You're welcome!",
        "Happy to help!",
        "Anytime! 😊"
    ],
    'question': [
        "That's a great question! Let me get back to you.",
        "Interesting question! I'll look into it.",
        "Good point! I'll check on that."
    ],
    'default': [
        "Thanks for your message! I'll respond soon.",
        "Got your message! Will get back to you shortly.",
        "Message received! I'll reply as soon as possible."
    ]
}

# Keyword triggers
KEYWORDS = {
    'greeting': ['hi', 'hello', 'hey', 'good morning', 'good evening'],
    'thanks': ['thanks', 'thank you', 'appreciate', 'grateful'],
    'question': ['?', 'how', 'what', 'when', 'where', 'why', 'who']
}

def get_response(message_text):
    """Get appropriate response based on message content"""
    message_lower = message_text.lower()
    
    # Check for keywords
    for category, keywords in KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            return random.choice(RESPONSE_TEMPLATES[category])
    
    # Default response
    return random.choice(RESPONSE_TEMPLATES['default'])

# Global state
bot_active = False
response_mode = None
away_message = None

async def auto_reply_bot():
    """
    Feature 112 (ENHANCED): Auto-reply bot with multi-account support - FIXED
    """
    global bot_active, response_mode, away_message
    
    try:
        print(f"\n{'-'*70}")
        print("⭐ AUTO-REPLY BOT")
        print(f"{'-'*70}\n")
        
        print("Account Options:")
        print("1. All accounts")
        print("2. Single account")
        
        account_choice = input("\nSelect option (1-2): ").strip()
        
        # Get accounts
        if account_choice == '1':
            clients_dict = await session_manager.get_all_clients()
        else:
            phone = input("Enter phone number: ").strip()
            client = await session_manager.get_client(phone)
            if not client:
                status.show_error("Account not found")
                return
            clients_dict = {phone: client}
        
        if not clients_dict:
            status.show_error("No active accounts found")
            return
        
        print("\nResponse Mode:")
        print("1. Template responses (keyword-based)")
        print("2. Custom away message")
        
        response_mode = input("\nSelect mode (1-2): ").strip()
        
        if response_mode == '2':
            away_message = input("Enter away message: ").strip()
        
        print(f"\n{'-'*70}")
        print(f"Accounts: {len(clients_dict)}")
        print(f"Mode: {['Template', 'Away Message'][int(response_mode)-1]}")
        print(f"Delay: 30-120 seconds before reply")
        print(f"{'-'*70}\n")
        
        print(f"Delay: 30-120 seconds before reply")
        print(f"{'-'*70}\n")
        
        confirm = input("Start auto-reply bot? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        await start_auto_reply_daemon(clients_dict, response_mode, away_message)
    except Exception as e:
        logger.error(f"Auto-reply setup error: {e}")

async def start_auto_reply_daemon(clients_dict, response_mode, away_message):
    """Headless entry point for auto reply bot"""
    global bot_active
    
    try:
        bot_active = True
        
        # Create event handlers for each client
        handlers = []
        
        for phone, client in clients_dict.items():
            # Create handler function with proper closure
            def make_handler(phone_num, client_obj, mode, msg):
                async def handler(event):
                    if not bot_active:
                        return
                    
                    try:
                        # Only respond to private messages
                        if not event.is_private:
                            return
                        
                        # Ignore messages from self
                        me = await client_obj.get_me()
                        if event.sender_id == me.id:
                            return
                        
                        # Random delay before reply (30-120 seconds)
                        delay = random.randint(30, 120)
                        logger.info(f"[{phone_num}] New message from {event.sender_id}, replying in {delay}s")
                        await asyncio.sleep(delay)
                        
                        # Get response
                        if mode == '1':
                            response = get_response(event.message.text or "")
                        else:
                            response = msg
                        
                        # Send reply
                        await event.respond(response)
                        
                        logger.success(f"[{phone_num}] Auto-replied to {event.sender_id}: {response}")
                        
                    except Exception as e:
                        logger.error(f"[{phone_num}] Auto-reply error: {e}")
                
                return handler
            
            # Create and register handler
            handler_func = make_handler(phone, client, response_mode, away_message)
            client.add_event_handler(handler_func, events.NewMessage(incoming=True))
            handlers.append((client, handler_func))
            
            logger.info(f"[{phone}] Auto-reply handler registered")
        
        logger.success("Auto-reply bot started!")
        logger.info("Press Ctrl+C to stop")
        
        # Keep running and maintain connections
        try:
            while bot_active:
                # Check connections every 30 seconds
                for phone, client in clients_dict.items():
                    try:
                        if not client.is_connected():
                            logger.warning(f"[{phone}] Reconnecting...")
                            await client.connect()
                    except Exception as e:
                        logger.error(f"[{phone}] Connection error: {e}")
                
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("Stopping auto-reply bot...")
        
        # Cleanup: remove event handlers
        bot_active = False
        for client, handler in handlers:
            try:
                client.remove_event_handler(handler)
            except Exception:
                pass
        
        logger.info("Auto-reply bot stopped")
        
    except Exception as e:
        logger.error(f"Auto-reply bot error: {e}")
        bot_active = False
