import yt_dlp
import os
import logging

logger = logging.getLogger(__name__)

class YoutubeDownloader:
    def __init__(self, download_path="downloads", proxy=None):
        self.download_path = download_path
        self.proxy = proxy
        
        # Ensure download directory exists
        os.makedirs(download_path, exist_ok=True)
        
        self.base_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(download_path, '%(id)s.%(ext)s'),
            'writethumbnail': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'postprocessors': [{
                'key': 'FFmpegEmbedSubtitle',
            }],
            'merge_output_format': 'mp4'
        }
        
        # Check for local ffmpeg in project root / bin
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_ffmpeg_dir = os.path.join(project_root, 'bin')
        
        if os.path.exists(os.path.join(local_ffmpeg_dir, 'ffmpeg.exe')):
            self.base_opts['ffmpeg_location'] = local_ffmpeg_dir
            logger.info(f"Using local FFmpeg from: {local_ffmpeg_dir}")
        elif self._check_ffmpeg():
            logger.info("Using system FFmpeg")
        else:
            logger.warning("FFmpeg not found! High quality video/audio merging may fail.")
        
        if proxy:
            self.base_opts['proxy'] = proxy

    def _check_ffmpeg(self):
        # Simple check if ffmpeg is available (can be improved)
        from shutil import which
        return which('ffmpeg') is not None

    def get_channel_videos(self, channel_url, limit=5):
        """
        Fetch metadata for the latest videos from a channel.
        Does not download the video files.
        """
        opts = self.base_opts.copy()
        opts['extract_flat'] = True  # Don't download, just extract info
        opts['playlistend'] = limit
        
        logger.info(f"Fetching videos from {channel_url}...")
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                if 'entries' in info:
                    # Filter out None entries if any
                    return [v for v in info['entries'] if v]
                return []
        except Exception as e:
            logger.error(f"Error fetching channel videos: {e}")
            return []

    def download_video(self, video_url, channel_name=None):
        """
        Download a specific video.
        Returns a dict with paths to video and thumbnail.
        """
        logger.info(f"Downloading video: {video_url}")
        
        # Prepare download path
        target_dir = self.download_path
        if channel_name:
            # Sanitize channel name to be safe for directory
            safe_channel_name = "".join([c for c in channel_name if c.isalnum() or c in (' ', '-', '_')]).strip()
            target_dir = os.path.join(self.download_path, safe_channel_name)
        
        os.makedirs(target_dir, exist_ok=True)
        
        # Copy base options and update output template
        opts = self.base_opts.copy()
        opts['outtmpl'] = os.path.join(target_dir, '%(id)s.%(ext)s')
        
        # Ensure best quality
        # bestvideo+bestaudio is already in base_opts, but we can make it more explicit if needed
        # opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' 
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                video_id = info['id']
                ext = info['ext']
                filename = f"{video_id}.{ext}"
                filepath = os.path.join(target_dir, filename)
                
                # Find thumbnail
                thumbnail_path = None
                # yt-dlp might download thumbnail as .jpg or .webp
                for potential_ext in ['jpg', 'webp', 'png']:
                    potential_path = os.path.join(target_dir, f"{video_id}.{potential_ext}")
                    if os.path.exists(potential_path):
                        thumbnail_path = potential_path
                        break
                
                return {
                    'filepath': filepath,
                    'thumbnail_path': thumbnail_path,
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'tags': info.get('tags', []),
                    'duration': info.get('duration')
                }
        except Exception as e:
            logger.error(f"Error downloading video {video_url}: {e}")
            raise e
