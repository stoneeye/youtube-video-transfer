import time
import logging
import asyncio
import os
import sys

# Add project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.orm import Session

from src.config_loader import get_config
from src.database import init_db, Video, Status
from src.downloader import YoutubeDownloader
from src.uploader import BilibiliUploader
from deep_translator import GoogleTranslator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("transfer.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_video(video_info, channel_config, session_factory, downloader, uploader):
    # Create a new session for this video processing to avoid long-lived session issues
    session = session_factory()
    try:
        video_id = video_info['id']
        # Construct URL if not present
        video_url = video_info.get('webpage_url') or f"https://www.youtube.com/watch?v={video_id}"
        
        # Check if exists in DB
        existing = session.query(Video).filter_by(youtube_id=video_id).first()
        
        if existing:
            if existing.status == Status.UPLOADED:
                logger.info(f"Video {video_id} already uploaded. Skipping.")
                return
            if existing.status == Status.DOWNLOADED:
                logger.info(f"Video {video_id} already downloaded. Skipping.")
                return
            if existing.status == Status.FAILED:
                logger.info(f"Video {video_id} previously failed. Retrying...")
                # Reset status to retry
                existing.status = Status.PENDING
                session.commit()
            elif existing.status == Status.PENDING:
                 logger.info(f"Video {video_id} is pending.")
        else:
            logger.info(f"Found new video: {video_id} - {video_info.get('title')}")
            new_video = Video(
                youtube_id=video_id,
                title=video_info.get('title'),
                url=video_url,
                status=Status.PENDING
            )
            session.add(new_video)
            session.commit()
            existing = new_video

        video_db_id = existing.id

        try:
            # 1. Download
            logger.info(f"Downloading video {video_id}...")
            existing.status = Status.DOWNLOADING
            session.commit()
            
            download_result = downloader.download_video(video_url, channel_name=channel_config.name)
            
            # Translate and format title
            original_title = download_result['title']
            try:
                translated_title = GoogleTranslator(source='auto', target='zh-CN').translate(original_title)
            except Exception as trans_e:
                logger.warning(f"Translation failed for '{original_title}': {trans_e}. Using original title.")
                translated_title = original_title
                
            formatted_title = f"【生肉】【{channel_config.name}】{translated_title}"
            
            existing.filepath = download_result['filepath']
            existing.thumbnail_path = download_result['thumbnail_path']
            existing.title = formatted_title # Update title with formatted version
            existing.status = Status.DOWNLOADED
            session.commit()
            
            logger.info(f"Video {video_id} downloaded successfully. Upload skipped.")
            
            # 2. Upload (Skipped)
            # logger.info(f"Uploading video {video_id}...")
            # existing.status = Status.UPLOADING
            # session.commit()
            
            # Use asyncio.run to execute async upload function
            # bvid = asyncio.run(uploader.upload_video(
            #     video_path=download_result['filepath'],
            #     title=formatted_title,
            #     description=download_result['description'],
            #     tid=channel_config.bilibili_tid,
            #     tags=download_result['tags'],
            #     source_url=video_url,
            #     cover_path=download_result['thumbnail_path']
            # ))
            
            # existing.bilibili_bvid = bvid
            # existing.status = Status.UPLOADED
            # existing.updated_at = datetime.utcnow()
            # session.commit()
            # logger.info(f"Video {video_id} processing complete!")
            
            # 3. Cleanup (Optional: remove file after upload)
            # os.remove(download_result['filepath'])
            
        except Exception as e:
            logger.error(f"Failed to process video {video_id}: {e}")
            existing.status = Status.FAILED
            existing.error_msg = str(e)
            session.commit()
            
    except Exception as e:
        logger.error(f"Critical error in process_video: {e}")
    finally:
        session.close()

def job():
    logger.info("Starting scheduled check...")
    try:
        config = get_config()
        SessionLocal = init_db()
        
        downloader = YoutubeDownloader(config.app.download_path, config.app.proxy)
        # uploader = BilibiliUploader(config.bilibili.sessdata, config.bilibili.bili_jct, config.bilibili.dedeuserid)
        uploader = None
        
        for channel_config in config.youtube_channels:
            logger.info(f"Checking channel: {channel_config.url}")
            try:
                videos = downloader.get_channel_videos(channel_config.url, limit=config.app.fetch_limit)
                for video_info in videos:
                    process_video(video_info, channel_config, SessionLocal, downloader, uploader)
            except Exception as e:
                logger.error(f"Error checking channel {channel_config.url}: {e}")
                
    except Exception as e:
        logger.error(f"Job failed: {e}")
    logger.info("Job finished.")

if __name__ == "__main__":
    print("Starting Video Transfer Service...")
    logger.info("Starting Video Transfer Service")
    
    # Initialize DB
    init_db()
    
    config = get_config()
    scheduler = BlockingScheduler()
    
    # Run once immediately
    scheduler.add_job(job, 'date', run_date=datetime.now())
    
    # Schedule interval
    scheduler.add_job(job, 'interval', seconds=config.app.check_interval)
    
    try:
        print(f"Service started. Checking every {config.app.check_interval} seconds.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Service stopped.")
