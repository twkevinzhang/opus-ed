from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Task, Metadata, Source, DownloadMode

class IMetadataProvider(ABC):
    @abstractmethod
    async def get_metadata(self, anime_title: str, token: Optional[str] = None) -> List[Metadata]:
        """從外部來源（如 Bangumi）獲取動畫的 OP/ED 資訊"""
        pass

class IDownloader(ABC):
    @abstractmethod
    async def download(self, task: Task) -> bool:
        """執行下載任務"""
        pass

    @abstractmethod
    def get_source(self) -> Source:
        """回傳此下載器支援的來源"""
        pass

class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None:
        """新增任務"""
        pass

    @abstractmethod
    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """按 ID 獲取任務"""
        pass

    @abstractmethod
    async def list_all(self) -> List[Task]:
        """列出所有任務"""
        pass

    @abstractmethod
    async def update(self, task: Task) -> None:
        """更新任務狀態"""
        pass

    @abstractmethod
    async def save_history(self, task: Task) -> None:
        """存入歷史紀錄"""
        pass
