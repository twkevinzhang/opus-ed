from typing import List, Optional
from sidecar.domain.models import Task, Metadata, Source, DownloadMode, TaskStatus
from sidecar.domain.repositories import IMetadataProvider, IDownloader, ITaskRepository

class CreateBatchTaskUseCase:
    def __init__(self, metadata_provider: IMetadataProvider, task_repo: ITaskRepository):
        self.metadata_provider = metadata_provider
        self.task_repo = task_repo

    async def execute(
        self, 
        titles: List[str], 
        target_dir: str, 
        source: Source, 
        dmhy_mode: DownloadMode,
        bangumi_token: Optional[str] = None
    ) -> List[Task]:
        """
        批次建立任務
        1. 獲取元數據
        2. 建立 Task 實體
        3. 儲存至 Reposiotry
        """
        new_tasks = []
        for title in titles:
            metas = await self.metadata_provider.get_metadata(title, token=bangumi_token)
            
            # 這裡採取一個動畫標題對應多個歌曲任務的邏輯（若 meta 有多筆）
            if not metas:
                # 即使沒找到 meta 也建立一個空 Task 供使用者手動編輯
                task = Task(anime_title=title, target_dir=target_dir, source=source, dmhy_mode=dmhy_mode)
                await self.task_repo.add(task)
                new_tasks.append(task)
            else:
                for meta in metas:
                    task = Task(
                        anime_title=meta.anime_title,
                        target_dir=target_dir,
                        source=source,
                        dmhy_mode=dmhy_mode,
                        metadata=meta
                    )
                    await self.task_repo.add(task)
                    new_tasks.append(task)
        
        return new_tasks

class DownloadTaskUseCase:
    def __init__(self, downloaders: List[IDownloader], task_repo: ITaskRepository):
        self.downloaders = {d.get_source(): d for d in downloaders}
        self.task_repo = task_repo

    async def execute(self, task_id: str) -> bool:
        """執行單個下載任務"""
        task = await self.task_repo.get_by_id(task_id)
        if not task: return False

        downloader = self.downloaders.get(task.source)
        if not downloader:
            task.update_status(TaskStatus.FAILED, error=f"未支援的下載來源: {task.source}")
            await self.task_repo.update(task)
            return False

        try:
            success = await downloader.download(task)
            await self.task_repo.update(task)
            if success:
                await self.task_repo.save_history(task)
            return success
        except Exception as e:
            task.update_status(TaskStatus.FAILED, error=str(e))
            await self.task_repo.update(task)
            return False
