from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import os

from sidecar.domain.models import Source, DownloadMode, TaskStatus, Source as SourceEnum
from sidecar.domain.repositories import IMetadataProvider, IDownloader, ITaskRepository
from sidecar.application.use_cases import CreateBatchTaskUseCase, DownloadTaskUseCase

from sidecar.infrastructure.metadata_provider import BangumiMetadataProvider
from sidecar.infrastructure.youtube_downloader import YouTubeDownloader
from sidecar.infrastructure.dmhy_downloader import DMHYDownloader
from sidecar.infrastructure.repositories import JSONTaskRepository

app = FastAPI(title="OpusED Sidecar API")

# 基礎設施實例 (Singleton-like patterns at app level)
metadata_provider = BangumiMetadataProvider()
task_repo = JSONTaskRepository()
downloaders = [YouTubeDownloader(), DMHYDownloader()]

# 用例實例
create_batch_use_case = CreateBatchTaskUseCase(metadata_provider, task_repo)
download_task_use_case = DownloadTaskUseCase(downloaders, task_repo)

class BatchCreateRequest(BaseModel):
    titles: List[str]
    target_dir: str
    source: str  # "youtube" or "dmhy"
    dmhy_mode: str = "video" # "video" or "torrent"
    bangumi_token: Optional[str] = None

class TaskUpdate(BaseModel):
    anime_title: Optional[str] = None
    target_dir: Optional[str] = None
    source: Optional[str] = None
    dmhy_mode: Optional[str] = None

@app.post("/tasks/batch")
async def create_batch(req: BatchCreateRequest):
    try:
        source_enum = Source(req.source)
        mode_enum = DownloadMode(req.dmhy_mode)
        tasks = await create_batch_use_case.execute(
            req.titles, req.target_dir, source_enum, mode_enum, req.bangumi_token
        )
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks")
async def list_tasks():
    return await task_repo.list_all()

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = await task_repo.get_by_id(task_id)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks/{task_id}/download")
async def start_download(task_id: str, background_tasks: BackgroundTasks):
    # 這裡使用 BackgroundTasks 進行非同步執行，不阻塞 API
    background_tasks.add_task(download_task_use_case.execute, task_id)
    return {"message": "Download started in background"}

@app.patch("/tasks/{task_id}")
async def update_task(task_id: str, update: TaskUpdate):
    task = await task_repo.get_by_id(task_id)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    
    if update.anime_title: task.anime_title = update.anime_title
    if update.target_dir: task.target_dir = update.target_dir
    if update.source: task.source = Source(update.source)
    if update.dmhy_mode: task.dmhy_mode = DownloadMode(update.dmhy_mode)
    
    await task_repo.update(task)
    return task

@app.get("/health")
def health_check():
    return {"status": "healthy"}
