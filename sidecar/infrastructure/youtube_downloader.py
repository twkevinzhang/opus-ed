import os
import asyncio
import logging
from typing import Optional, Dict, Any
import yt_dlp
from sidecar.domain.models import Task, TaskStatus, Source

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def get_source(self) -> Source:
        return Source.YOUTUBE

    async def download(self, task: Task) -> bool:
        """使用 yt-dlp 下載影片/音訊"""
        if not task.metadata or not task.metadata.song_title:
            task.update_status(TaskStatus.FAILED, error="缺少元數據，無法搜尋下載")
            return False

        search_query = f"{task.metadata.anime_title} {task.metadata.song_title} {task.metadata.type}"
        # 如果有手動指定的關鍵字，優先使用
        if hasattr(task, 'custom_keywords') and task.custom_keywords:
            search_query = task.custom_keywords

        os.makedirs(task.target_dir, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(task.target_dir, '%(title)s.%(ext)s'),
            'logger': MyYtdlpLogger(task),
            'progress_hooks': [lambda d: self._progress_hook(d, task)],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }

        task.update_status(TaskStatus.DOWNLOADING, progress=1.0)
        
        try:
            loop = asyncio.get_event_loop()
            # 在執行緒池中執行，避免阻塞事件迴圈
            await loop.run_in_executor(None, self._run_ytdl, f"ytsearch1:{search_query}", ydl_opts)
            
            # 檢查檔案是否真的存在（yt-dlp 有時會安靜地失敗）
            if task.status != TaskStatus.FAILED:
                task.update_status(TaskStatus.COMPLETED, progress=100.0)
                return True
            return False
        except Exception as e:
            logger.error(f"YouTube 下載失敗: {e}")
            task.update_status(TaskStatus.FAILED, error=f"下載失敗: {str(e)}")
            return False

    def _run_ytdl(self, url: str, opts: Dict[str, Any]):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except Exception as e:
            raise e

    def _progress_hook(self, d: Dict[str, Any], task: Task):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                progress = (downloaded_bytes / total_bytes) * 100
                task.update_status(TaskStatus.DOWNLOADING, progress=round(progress, 1))

class MyYtdlpLogger:
    def __init__(self, task: Task):
        self.task = task
    def debug(self, msg: str):
        if msg.startswith('[debug] '): pass
        else: logger.debug(msg)
    def warning(self, msg: str):
        logger.warning(msg)
    def error(self, msg: str):
        logger.error(msg)
        # 不要在這裡直接設為 FAILED，因為有些 error 可能不致命或由 YoutubeDL catch
