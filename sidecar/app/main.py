from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
import asyncio

# 配置 Root Logger 為 INFO
logging.basicConfig(level=logging.INFO)

from sidecar.domain.models import Source, DownloadMode, TaskStatus, Task, Metadata
from sidecar.application.use_cases import DownloadTaskUseCase, SearchMetadataUseCase
from sidecar.infrastructure.metadata_provider import BangumiMetadataProvider
from sidecar.infrastructure.youtube_downloader import YouTubeDownloader
from sidecar.infrastructure.dmhy_downloader import DMHYDownloader
from sidecar.infrastructure.task_manager import TaskManager

app = FastAPI(title="OpusED Sidecar API (Stateless)")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基礎設施實例
metadata_provider = BangumiMetadataProvider()
downloaders = [YouTubeDownloader(), DMHYDownloader()]
task_manager = TaskManager.get_instance()

# 用例實例
download_task_use_case = DownloadTaskUseCase(downloaders)
search_metadata_use_case = SearchMetadataUseCase(metadata_provider)

class SearchRequest(BaseModel):
    title: str
    token: Optional[str] = None

class DownloadRequest(BaseModel):
    # 此 Request 結構應與 Task Domain Model 保持一致
    task_id: str  # 由 Electron 傳入，確保兩端 ID 一致
    anime_title: str
    target_dir: str
    source: str
    dmhy_mode: str = "video"
    metadata: Optional[dict] = None
    custom_keywords: Optional[str] = None

@app.get("/metadata/search")
async def search_metadata(title: str, token: Optional[str] = None):
    """提供搜尋服務介面"""
    return await search_metadata_use_case.execute(title, token=token)

async def _execute_download_background(task: Task) -> None:
    """背景執行下載任務。"""
    logger = logging.getLogger(__name__)
    logger.info(f"[Background] Starting download for task {task.id}")
    try:
        await download_task_use_case.execute(task)
        logger.info(f"[Background] Download completed for task {task.id}, status={task.status.value}")
    except Exception as e:
        logger.error(f"[Background] Download failed for task {task.id}: {e}")
        task.update_status(TaskStatus.FAILED, error=str(e))


@app.post("/download")
async def execute_download(req: DownloadRequest):
    """
    啟動下載任務（異步）。
    立即返回 task_id，客戶端可通過 GET /tasks/{task_id}/status 輪詢進度。
    """
    try:
        # 重建 Task 實體用於下載器
        task_metadata = None
        if req.metadata:
            task_metadata = Metadata(**req.metadata)

        task = Task(
            id=req.task_id,  # 使用客戶端傳入的 ID
            anime_title=req.anime_title,
            target_dir=req.target_dir,
            source=Source(req.source),
            dmhy_mode=DownloadMode(req.dmhy_mode),
            metadata=task_metadata,
            custom_keywords=req.custom_keywords
        )

        # 將任務加入管理器
        task_manager.add_task(task)
        logging.info(f"[/download] Task {task.id} added to TaskManager, total tasks: {len(task_manager.get_all_tasks())}")

        # 異步啟動下載（不等待完成）
        asyncio.create_task(_execute_download_background(task))

        return {
            "task_id": task.id,
            "status": task.status.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """查詢單個任務的狀態和進度。"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return {
        "task_id": task.id,
        "status": task.status.value,
        "progress": task.progress,
        "error_message": task.error_message
    }


@app.get("/tasks")
async def get_all_tasks():
    """查詢所有活躍任務的狀態。"""
    tasks = task_manager.get_all_tasks()
    logging.info(f"[/tasks] Returning {len(tasks)} tasks")
    return [
        {
            "task_id": t.id,
            "anime_title": t.anime_title,
            "status": t.status.value,
            "progress": t.progress,
            "error_message": t.error_message,
            "source": t.source.value,
            "target_dir": t.target_dir,
            "metadata": {
                "anime_title": t.metadata.anime_title,
                "song_title": t.metadata.song_title,
                "artist": t.metadata.artist,
                "type": t.metadata.type,
            } if t.metadata else None
        }
        for t in tasks
    ]


@app.delete("/tasks/{task_id}")
async def remove_task(task_id: str):
    """從管理器中移除任務。"""
    success = task_manager.remove_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"success": True}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "OpusED-Sidecar"}
