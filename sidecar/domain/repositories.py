from abc import ABC, abstractmethod
from typing import List, Optional
from sidecar.domain.models import Metadata, Task, Source

class IMetadataProvider(ABC):
    @abstractmethod
    async def get_metadata(self, anime_title: str, token: Optional[str] = None) -> List[Metadata]:
        pass

class IDownloader(ABC):
    @abstractmethod
    def get_source(self) -> Source:
        pass

    @abstractmethod
    async def download(self, task: Task) -> bool:
        pass
