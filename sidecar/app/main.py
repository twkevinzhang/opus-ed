from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

from sidecar.domain.models import Source, DownloadMode, TaskStatus, Task, Metadata
from sidecar.application.use_cases import DownloadTaskUseCase, SearchMetadataUseCase
from sidecar.infrastructure.metadata_provider import BangumiMetadataProvider
from sidecar.infrastructure.youtube_downloader import YouTubeDownloader
from sidecar.infrastructure.dmhy_downloader import DMHYDownloader

app = FastAPI(title="OpusED Sidecar API (Stateless)")

# 基礎設施實例
metadata_provider = BangumiMetadataProvider()
downloaders = [YouTubeDownloader(), DMHYDownloader()]

# 用例實例
download_task_use_case = DownloadTaskUseCase(downloaders)
search_metadata_use_case = SearchMetadataUseCase(metadata_provider)

class SearchRequest(BaseModel):
    title: str
    token: Optional[str] = None

class DownloadRequest(BaseModel):
    # 此 Request 結構應與 Task Domain Model 保持一致
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

@app.post("/download")
async def execute_download(req: DownloadRequest):
    """
    執行單次下載任務 (無狀態)。
    由 Electron 傳入完整任務資訊，Sidecar 僅負責背景執行並回傳即時狀態。
    注意：此處為簡化版實作，正式版可考慮使用 WebSocket 回傳進度。
    """
    try:
        # 重建 Task 實體用於下載器
        task_metadata = None
        if req.metadata:
            task_metadata = Metadata(**req.metadata)
            
        task = Task(
            anime_title=req.anime_title,
            target_dir=req.target_dir,
            source=Source(req.source),
            dmhy_mode=DownloadMode(req.dmhy_mode),
            metadata=task_metadata,
            custom_keywords=req.custom_keywords
        )
        
        success = await download_task_use_case.execute(task)
        
        return {
            "success": success,
            "task_id": task.id,
            "status": task.status.value,
            "progress": task.progress,
            "error_message": task.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "OpusED-Sidecar", "stateless": True}
