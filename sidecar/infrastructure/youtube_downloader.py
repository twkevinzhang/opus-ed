import os
import asyncio
from typing import Optional
import yt_dlp
from sidecar.domain.models import Task, TaskStatus, Source
from sidecar.domain.repositories import IDownloader

class YouTubeDownloader(IDownloader):
    def get_source(self) -> Source:
        return Source.YOUTUBE

    async def download(self, task: Task) -> bool:
        """使用 yt-dlp 下載影片/音訊"""
        if not task.metadata or not task.metadata.song_title:
            task.update_status(TaskStatus.FAILED, error="缺少元數據，無法搜尋下載")
            return False

        search_query = f"{task.metadata.anime_title} {task.metadata.song_title} {task.metadata.type}"
        os.makedirs(task.target_dir, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmp': os.path.join(task.target_dir, '%(title)s.%(ext)s'),
            'logger': MyLogger(task),
            'progress_hooks': [lambda d: self._progress_hook(d, task)],
        }

        # 搜尋第一個結果並下載
        task.update_status(TaskStatus.DOWNLOADING, progress=0.1)
        
        try:
            # 在 thread pool 中執行阻塞的 yt-dlp 調用
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self._run_ytdl(f"ytsearch1:{search_query}", ydl_opts))
            
            task.update_status(TaskStatus.COMPLETED, progress=100.0)
            return True
        except Exception as e:
            task.update_status(TaskStatus.FAILED, error=str(e))
            return False

    def _run_ytdl(self, url: str, opts: dict):
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    def _progress_hook(self, d, task: Task):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '')
            try:
                task.update_status(TaskStatus.DOWNLOADING, progress=float(p))
            except:
                pass

class MyLogger:
    def __init__(self, task: Task):
        self.task = task
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg):
        self.task.update_status(TaskStatus.FAILED, error=msg)
