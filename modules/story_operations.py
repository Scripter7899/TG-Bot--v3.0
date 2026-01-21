"""
Story Operations Module
Telegram Stories features
"""

import asyncio
from telethon.tl.functions.stories import SendStoryRequest, DeleteStoriesRequest, GetStoriesViewsRequest
from telethon.tl.types import InputMediaUploadedPhoto, InputMediaUploadedDocument
from core.session_manager import session_manager
from core.logger import logger
from ui.progress import StatusIndicator
from datetime import datetime
import config
from pathlib import Path

status = StatusIndicator()

async def view_stories():
    """View Stories from users/channels"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter username to view stories: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(target)
        
        # Get stories
        from telethon.tl.functions.stories import GetPeerStoriesRequest
        stories_result = await client(GetPeerStoriesRequest(peer=entity))
        
        if not stories_result.stories.stories:
            print(f"\n{target} has no active stories\n")
            status.show_success("No stories found")
            return
        
        print(f"\n{'='*70}")
        print(f"STORIES FROM: {target}")
        print(f"{'='*70}\n")
        
        for idx, story in enumerate(stories_result.stories.stories, 1):
            print(f"Story {idx}:")
            print(f"  ID: {story.id}")
            print(f"  Date: {story.date}")
            print(f"  Views: {story.views.views_count if hasattr(story, 'views') and story.views else 'N/A'}")
            print(f"  Media: {'Yes' if story.media else 'No'}")
            print(f"{'-'*70}")
        
        print(f"\nTotal Stories: {len(stories_result.stories.stories)}\n")
        status.show_success(f"Found {len(stories_result.stories.stories)} stories")
        
    except Exception as e:
        logger.error(f"Failed to view stories: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def post_story():
    """Post a Story"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        print("\nStory Type:")
        print("1. Text Story")
        print("2. Photo Story")
        print("3. Video Story")
        story_type = input("Select type (1-3): ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        if story_type == '1':
            # Text story
            text = input("Enter story text: ").strip()
            
            from telethon.tl.types import InputMediaStory
            # Note: Text-only stories require special handling
            print("\nNote: Text-only stories require media background. Using default.")
            status.show_error("Text-only stories not fully supported by Telegram API")
            
        elif story_type == '2':
            # Photo story
            photo_path = input("Enter photo path: ").strip()
            caption = input("Enter caption (optional): ").strip()
            
            if not Path(photo_path).exists():
                status.show_error("Photo file not found")
                return
            
            # Upload photo
            uploaded_file = await client.upload_file(photo_path)
            
            from telethon.tl.types import InputMediaUploadedPhoto, InputPeerSelf
            from telethon.tl.functions.stories import SendStoryRequest
            
            result = await client(SendStoryRequest(
                peer=InputPeerSelf(),
                media=InputMediaUploadedPhoto(file=uploaded_file),
                caption=caption,
                privacy_rules=[]
            ))
            
            logger.success("Photo story posted successfully")
            status.show_success("Story posted!")
            
        elif story_type == '3':
            # Video story
            video_path = input("Enter video path: ").strip()
            caption = input("Enter caption (optional): ").strip()
            
            if not Path(video_path).exists():
                status.show_error("Video file not found")
                return
            
            # Upload video
            uploaded_file = await client.upload_file(video_path)
            
            from telethon.tl.types import InputMediaUploadedDocument, InputPeerSelf, DocumentAttributeVideo
            from telethon.tl.functions.stories import SendStoryRequest
            
            result = await client(SendStoryRequest(
                peer=InputPeerSelf(),
                media=InputMediaUploadedDocument(
                    file=uploaded_file,
                    mime_type='video/mp4',
                    attributes=[DocumentAttributeVideo(duration=0, w=720, h=1280)]
                ),
                caption=caption,
                privacy_rules=[]
            ))
            
            logger.success("Video story posted successfully")
            status.show_success("Story posted!")
        
    except Exception as e:
        logger.error(f"Failed to post story: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def delete_story():
    """Delete own Story"""
    try:
        phone = input("Enter your phone number: ").strip()
        story_id = int(input("Enter story ID to delete: ").strip())
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        from telethon.tl.functions.stories import DeleteStoriesRequest
        
        await client(DeleteStoriesRequest(id=[story_id]))
        
        logger.success(f"Story {story_id} deleted")
        status.show_success("Story deleted successfully")
        
    except Exception as e:
        logger.error(f"Failed to delete story: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def story_analytics():
    """View Story Analytics"""
    try:
        phone = input("Enter your phone number: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        # Get own stories
        from telethon.tl.functions.stories import GetPeerStoriesRequest
        from telethon.tl.types import InputPeerSelf
        
        stories_result = await client(GetPeerStoriesRequest(peer=InputPeerSelf()))
        
        if not stories_result.stories.stories:
            print("\nYou have no active stories\n")
            status.show_success("No stories to analyze")
            return
        
        print(f"\n{'='*70}")
        print("YOUR STORY ANALYTICS")
        print(f"{'='*70}\n")
        
        total_views = 0
        for idx, story in enumerate(stories_result.stories.stories, 1):
            views = story.views.views_count if hasattr(story, 'views') and story.views else 0
            total_views += views
            
            print(f"Story {idx} (ID: {story.id}):")
            print(f"  Posted: {story.date}")
            print(f"  Views: {views}")
            print(f"  Forwards: {story.views.forwards_count if hasattr(story, 'views') and story.views and hasattr(story.views, 'forwards_count') else 0}")
            print(f"  Reactions: {story.views.reactions_count if hasattr(story, 'views') and story.views and hasattr(story.views, 'reactions_count') else 0}")
            print(f"{'-'*70}")
        
        print(f"\nTotal Stories: {len(stories_result.stories.stories)}")
        print(f"Total Views: {total_views}")
        print(f"Average Views: {total_views // len(stories_result.stories.stories) if stories_result.stories.stories else 0}\n")
        
        status.show_success("Analytics retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get story analytics: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")

async def download_stories():
    """Download Stories from users/channels"""
    try:
        phone = input("Enter your phone number: ").strip()
        target = input("Enter username to download stories from: ").strip()
        
        client = await session_manager.get_client(phone)
        if not client:
            status.show_error("Account not found")
            return
        
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_entity(target)
        
        # Get stories
        from telethon.tl.functions.stories import GetPeerStoriesRequest
        stories_result = await client(GetPeerStoriesRequest(peer=entity))
        
        if not stories_result.stories.stories:
            print(f"\n{target} has no active stories\n")
            status.show_success("No stories to download")
            return
        
        # Create download directory
        download_dir = config.EXPORTS_DIR / f"stories_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        download_dir.mkdir(parents=True, exist_ok=True)
        
        status.show_processing(f"Downloading {len(stories_result.stories.stories)} stories...")
        
        downloaded = 0
        for idx, story in enumerate(stories_result.stories.stories, 1):
            if story.media:
                try:
                    file_path = download_dir / f"story_{story.id}_{idx}"
                    await client.download_media(story.media, file=str(file_path))
                    downloaded += 1
                    print(f"Downloaded story {idx}/{len(stories_result.stories.stories)}")
                except Exception as e:
                    logger.error(f"Failed to download story {idx}: {e}")
        
        logger.success(f"Downloaded {downloaded} stories to {download_dir}")
        status.show_success(f"Downloaded {downloaded} stories")
        
    except Exception as e:
        logger.error(f"Failed to download stories: {e}")
        status.show_error(f"Failed: {str(e)}")
    finally:
        input("\nPress Enter to continue...")
