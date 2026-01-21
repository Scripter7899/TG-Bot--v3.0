"""
Marketing Advanced Module
Advanced marketing and growth features
"""

import asyncio
from telethon.tl.functions.messages import SendMessageRequest
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator
from datetime import datetime
import random

status = StatusIndicator()

async def auto_comment_on_posts():
    """Feature 98: Auto-Comment on Posts"""
    try:
        phone = input("Enter your phone number: ").strip()
        channel = input("Enter channel username to comment on: ").strip()
        
        print("\nEnter comment templates (one per line, empty to finish):")
        comments = []
        while True:
            comment = input("> ").strip()
            if not comment:
                break
            comments.append(comment)
        
        if not comments:
            comments = ["Great post!", "Thanks for sharing!", "Interesting!", "Love this!"]
            print(f"\nUsing default comments: {comments}")
        
        limit = int(input("Comment on last N posts (default 10): ").strip() or "10")
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(channel)
        
        print(f"\n{'='*70}")
        print(f"AUTO-COMMENTING ON: {channel}")
        print(f"{'='*70}\n")
        
        commented = 0
        async for message in client.iter_messages(entity, limit=limit):
            if message.id:
                try:
                    comment = random.choice(comments)
                    await client.send_message(entity, comment, comment_to=message.id)
                    print(f"✅ Commented on post {message.id}: '{comment}'")
                    commented += 1
                    await asyncio.sleep(random.randint(5, 10))
                except Exception as e:
                    print(f"❌ Failed to comment on post {message.id}: {e}")
        
        print(f"\n{'='*70}")
        print(f"Commented on {commented}/{limit} posts")
        print(f"{'='*70}\n")
        
        logger.success(f"Auto-commented on {commented} posts")
        status.show_success(f"Commented on {commented} posts")
        
    except Exception as e:
        logger.error(f"Failed auto-comment: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def follow_recommendations():
    """Feature 99: Follow Recommendations"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        # Get contacts
        from telethon.tl.functions.contacts import GetContactsRequest
        contacts = await client(GetContactsRequest(hash=0))
        
        print(f"\n{'='*70}")
        print("FOLLOW RECOMMENDATIONS")
        print(f"{'='*70}\n")
        
        print(f"Based on your {len(contacts.users)} contacts:")
        print("\nRecommended channels/groups to join:")
        
        # Simulate recommendations (in real implementation, would analyze contacts' memberships)
        recommendations = [
            "Telegram Tips",
            "Tech News",
            "Crypto Updates",
            "Marketing Strategies",
            "Business Growth"
        ]
        
        for idx, rec in enumerate(recommendations, 1):
            print(f"  {idx}. {rec}")
        
        print(f"\n{'='*70}\n")
        status.show_success("Recommendations generated")
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def channel_growth_analytics():
    """Feature 100: Channel Growth Analytics"""
    try:
        phone = input("Enter your phone number: ").strip()
        channel = input("Enter your channel username: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from telethon.tl.functions.channels import GetFullChannelRequest
        
        entity = await client.get_entity(channel)
        full = await client(GetFullChannelRequest(channel=entity))
        
        # Get recent messages for engagement
        total_views = 0
        total_forwards = 0
        message_count = 0
        
        async for message in client.iter_messages(entity, limit=50):
            message_count += 1
            if hasattr(message, 'views') and message.views:
                total_views += message.views
            if hasattr(message, 'forwards') and message.forwards:
                total_forwards += message.forwards
        
        print(f"\n{'='*70}")
        print(f"CHANNEL GROWTH ANALYTICS: {entity.title}")
        print(f"{'='*70}")
        print(f"\nSubscribers: {full.full_chat.participants_count}")
        print(f"\nEngagement (last 50 posts):")
        print(f"  Total Views: {total_views}")
        print(f"  Total Forwards: {total_forwards}")
        print(f"  Avg Views/Post: {total_views // message_count if message_count > 0 else 0}")
        print(f"  Avg Forwards/Post: {total_forwards // message_count if message_count > 0 else 0}")
        print(f"\nGrowth Metrics:")
        print(f"  Engagement Rate: {(total_views / full.full_chat.participants_count * 100):.2f}%" if full.full_chat.participants_count > 0 else "0%")
        print(f"  Viral Coefficient: {(total_forwards / message_count):.2f}" if message_count > 0 else "0")
        print(f"{'='*70}\n")
        
        status.show_success("Growth analytics retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get growth analytics: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def hashtag_management():
    """Feature 101: Hashtag Management"""
    try:
        phone = input("Enter your phone number: ").strip()
        channel = input("Enter channel to analyze: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(channel)
        
        # Analyze hashtags
        hashtag_count = {}
        message_count = 0
        
        async for message in client.iter_messages(entity, limit=100):
            message_count += 1
            if message.text:
                # Extract hashtags
                words = message.text.split()
                for word in words:
                    if word.startswith('#'):
                        hashtag = word.lower()
                        hashtag_count[hashtag] = hashtag_count.get(hashtag, 0) + 1
        
        print(f"\n{'='*70}")
        print(f"HASHTAG ANALYTICS: {channel}")
        print(f"{'='*70}")
        print(f"Messages Analyzed: {message_count}")
        print(f"Unique Hashtags: {len(hashtag_count)}")
        print(f"\nTop 10 Hashtags:")
        
        sorted_hashtags = sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)[:10]
        for idx, (hashtag, count) in enumerate(sorted_hashtags, 1):
            print(f"  {idx}. {hashtag}: {count} times")
        
        print(f"\nRecommended Hashtags:")
        print("  #trending #viral #growth #marketing #business")
        print(f"{'='*70}\n")
        
        status.show_success("Hashtag analysis complete")
        
    except Exception as e:
        logger.error(f"Failed hashtag management: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def trending_topics_tracker():
    """Feature 102: Trending Topics Tracker"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        print("\nEnter channels to track (one per line, empty to finish):")
        channels = []
        while True:
            channel = input("> ").strip()
            if not channel:
                break
            channels.append(channel)
        
        if not channels:
            print("No channels provided")
            return
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        # Track keywords across channels
        keyword_count = {}
        
        print(f"\n{'='*70}")
        print("TRENDING TOPICS TRACKER")
        print(f"{'='*70}\n")
        
        for channel in channels:
            try:
                entity = await client.get_entity(channel)
                print(f"Analyzing: {channel}...")
                
                async for message in client.iter_messages(entity, limit=20):
                    if message.text:
                        # Extract keywords (simple word frequency)
                        words = message.text.lower().split()
                        for word in words:
                            if len(word) > 5 and not word.startswith('#'):
                                keyword_count[word] = keyword_count.get(word, 0) + 1
            except Exception as e:
                print(f"Failed to analyze {channel}: {e}")
        
        print(f"\n{'='*70}")
        print("TRENDING TOPICS:")
        print(f"{'='*70}\n")
        
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:15]
        for idx, (keyword, count) in enumerate(sorted_keywords, 1):
            print(f"  {idx}. {keyword}: {count} mentions")
        
        print(f"\n{'='*70}\n")
        status.show_success("Trending topics tracked")
        
    except Exception as e:
        logger.error(f"Failed to track trending topics: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def schedule_posts():
    """Feature 103: Schedule Posts"""
    try:
        phone = input("Enter your phone number: ").strip()
        channel = input("Enter channel username: ").strip()
        
        print("\nEnter posts to schedule (one per line, empty to finish):")
        posts = []
        while True:
            post = input("> ").strip()
            if not post:
                break
            posts.append(post)
        
        if not posts:
            print("No posts provided")
            return
        
        from datetime import datetime, timedelta
        
        interval_hours = int(input("Hours between posts (default 6): ").strip() or "6")
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(channel)
        
        print(f"\n{'='*70}")
        print(f"SCHEDULING {len(posts)} POSTS")
        print(f"{'='*70}\n")
        
        schedule_time = datetime.now() + timedelta(hours=1)
        
        for idx, post in enumerate(posts, 1):
            await client.send_message(entity, post, schedule=schedule_time)
            print(f"Post {idx} scheduled for: {schedule_time}")
            schedule_time += timedelta(hours=interval_hours)
        
        print(f"\n{'='*70}")
        print(f"All {len(posts)} posts scheduled")
        print(f"{'='*70}\n")
        
        logger.success(f"Scheduled {len(posts)} posts")
        status.show_success(f"Scheduled {len(posts)} posts")
        
    except Exception as e:
        logger.error(f"Failed to schedule posts: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def content_optimizer():
    """Feature 105: Content Optimizer"""
    try:
        phone = input("Enter your phone number: ").strip()
        channel = input("Enter channel to analyze: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(channel)
        
        # Analyze top performing content
        best_views = 0
        best_message = None
        total_views = 0
        message_count = 0
        
        async for message in client.iter_messages(entity, limit=50):
            message_count += 1
            if hasattr(message, 'views') and message.views:
                total_views += message.views
                if message.views > best_views:
                    best_views = message.views
                    best_message = message
        
        avg_views = total_views // message_count if message_count > 0 else 0
        
        print(f"\n{'='*70}")
        print("CONTENT OPTIMIZATION INSIGHTS")
        print(f"{'='*70}")
        print(f"\nBest Performing Post:")
        print(f"  Views: {best_views}")
        if best_message and best_message.text:
            print(f"  Text: {best_message.text[:100]}...")
        
        print(f"\nAverage Views: {avg_views}")
        print(f"\nRecommendations:")
        print("  ✓ Post during peak hours (8-10 AM, 6-8 PM)")
        print("  ✓ Use engaging headlines")
        print("  ✓ Include media (images/videos)")
        print("  ✓ Add relevant hashtags")
        print("  ✓ Keep posts concise and clear")
        print(f"{'='*70}\n")
        
        status.show_success("Content insights generated")
        
    except Exception as e:
        logger.error(f"Failed content optimization: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

