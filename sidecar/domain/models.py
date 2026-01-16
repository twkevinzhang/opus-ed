from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime
import uuid

class Source(Enum):
    YOUTUBE = "youtube"
    DMHY = "dmhy"

class DownloadMode(Enum):
    VIDEO = "video"
    TORRENT = "torrent"  # 僅適用於 DMHY

class TaskStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass(frozen=True)
class Metadata:
    anime_title: str
    song_title: str
    artist: str
    type: str  # e.g., "OP", "ED"
    bangumi_id: Optional[str] = None

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    anime_title: str = ""
    target_dir: str = ""
    source: Source = Source.YOUTUBE
    dmhy_mode: DownloadMode = DownloadMode.VIDEO
    metadata: Optional[Metadata] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_status(self, status: TaskStatus, progress: float = 0.0, error: Optional[str] = None):
        self.status = status
        self.progress = progress
        self.error_message = error
        self.updated_at = datetime.now()
