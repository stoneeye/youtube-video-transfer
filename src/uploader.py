import logging
import asyncio
from bilibili_api import Credential, video_uploader
from bilibili_api.video_uploader import VideoUploaderPage

logger = logging.getLogger(__name__)

class BilibiliUploader:
    def __init__(self, sessdata, bili_jct, dedeuserid):
        self.credential = Credential(sessdata=sessdata, bili_jct=bili_jct, dedeuserid=dedeuserid)

    async def upload_video(self, video_path, title, description, tid, tags, source_url, cover_path=None):
        """
        Uploads a video to Bilibili.
        Returns the BVID of the uploaded video.
        """
        logger.info(f"Starting upload for: {title}")
        try:
            # Create video page
            # Note: Bilibili might have title length limit (80 chars)
            safe_title = title[:80]
            page = VideoUploaderPage(path=video_path, title=safe_title)
            
            # Prepare metadata
            meta = {
                'copyright': 2,  # 1=Original, 2=Reprint
                'source': source_url,
                'desc': description[:2000] if description else "No description",  # Limit description length
                'use_mission': False,
                'tag': ','.join(tags[:10]) if isinstance(tags, list) else tags, # Limit tags count
                'tid': tid,
            }
            
            # Initialize uploader
            uploader = video_uploader.VideoUploader([page], meta, self.credential, cover=cover_path)
            
            # Optional: Add progress listener
            @uploader.on("PROGRESS")
            async def on_progress(data):
                # Log progress periodically if needed
                pass

            # Start upload
            info = await uploader.start()
            bvid = info.get('bvid')
            logger.info(f"Upload successful! BVID: {bvid}")
            return bvid
            
        except Exception as e:
            logger.error(f"Error uploading video {title}: {e}")
            raise e
