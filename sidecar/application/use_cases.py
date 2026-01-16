from typing import List, Optional
from sidecar.domain.models import Task, Metadata, Source, DownloadMode, TaskStatus
from sidecar.domain.repositories import IMetadataProvider, IDownloader

class SearchMetadataUseCase:
    def __init__(self, metadata_provider: IMetadataProvider):
        self.metadata_provider = metadata_provider

    async def execute(self, title: str, token: Optional[str] = None) -> List[Metadata]:
        """純搜尋動畫元數據"""
        return await self.metadata_provider.get_metadata(title, token=token)

class DownloadTaskUseCase:
    def __init__(self, downloaders: List[IDownloader]):
        self.downloaders = {d.get_source(): d for d in downloaders}

    async def execute(self, task: Task) -> bool:
        """執行單個下載任務。Sidecar 現在僅負責執行，不負責狀態管理或儲存。"""
        downloader = self.downloaders.get(task.source)
        if not downloader:
            task.update_status(TaskStatus.FAILED, error=f"未支援的下載來源: {task.source}")
            return False

        try:
            # 執行下載
            success = await downloader.download(task)
            return success
        except Exception as e:
            task.update_status(TaskStatus.FAILED, error=str(e))
            return False
