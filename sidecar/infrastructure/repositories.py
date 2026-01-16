import json
import os
import asyncio
from typing import List, Optional, Dict
from datetime import datetime
from sidecar.domain.models import Task, Metadata, Source, DownloadMode, TaskStatus
from sidecar.domain.repositories import ITaskRepository

class JSONTaskRepository(ITaskRepository):
    def __init__(self, tasks_path: str = "sidecar/data/tasks.json", history_path: str = "sidecar/data/download_history.json"):
        self.tasks_path = tasks_path
        self.history_path = history_path
        self._lock = asyncio.Lock()
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(tasks_path), exist_ok=True)
        os.makedirs(os.path.dirname(history_path), exist_ok=True)

    def _serialize_task(self, task: Task) -> dict:
        data = {
            "id": task.id,
            "anime_title": task.anime_title,
            "target_dir": task.target_dir,
            "source": task.source.value,
            "dmhy_mode": task.dmhy_mode.value,
            "status": task.status.value,
            "progress": task.progress,
            "error_message": task.error_message,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
        if task.metadata:
            data["metadata"] = {
                "anime_title": task.metadata.anime_title,
                "song_title": task.metadata.song_title,
                "artist": task.metadata.artist,
                "type": task.metadata.type,
                "bangumi_id": task.metadata.bangumi_id
            }
        return data

    def _deserialize_task(self, data: dict) -> Task:
        metadata = None
        if "metadata" in data and data["metadata"]:
            m = data["metadata"]
            metadata = Metadata(
                anime_title=m["anime_title"],
                song_title=m["song_title"],
                artist=m["artist"],
                type=m["type"],
                bangumi_id=m.get("bangumi_id")
            )
        
        task = Task(
            id=data["id"],
            anime_title=data["anime_title"],
            target_dir=data["target_dir"],
            source=Source(data["source"]),
            dmhy_mode=DownloadMode(data["dmhy_mode"]),
            metadata=metadata,
            status=TaskStatus(data["status"]),
            progress=data["progress"],
            error_message=data.get("error_message"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        return task

    async def _load_file(self, path: str) -> List[dict]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                return json.loads(content) if content else []
        except:
            return []

    async def _save_file(self, path: str, data: List[dict]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def add(self, task: Task) -> None:
        async with self._lock:
            tasks = await self._load_file(self.tasks_path)
            tasks.append(self._serialize_task(task))
            await self._save_file(self.tasks_path, tasks)

    async def get_by_id(self, task_id: str) -> Optional[Task]:
        async with self._lock:
            tasks = await self._load_file(self.tasks_path)
            for t_data in tasks:
                if t_data["id"] == task_id:
                    return self._deserialize_task(t_data)
        return None

    async def list_all(self) -> List[Task]:
        async with self._lock:
            tasks = await self._load_file(self.tasks_path)
            return [self._deserialize_task(t) for t in tasks]

    async def update(self, task: Task) -> None:
        async with self._lock:
            tasks = await self._load_file(self.tasks_path)
            updated_tasks = []
            for t_data in tasks:
                if t_data["id"] == task.id:
                    updated_tasks.append(self._serialize_task(task))
                else:
                    updated_tasks.append(t_data)
            await self._save_file(self.tasks_path, updated_tasks)

    async def save_history(self, task: Task) -> None:
        async with self._lock:
            history = await self._load_file(self.history_path)
            history.append(self._serialize_task(task))
            await self._save_file(self.history_path, history)

            # 同時從活躍任務中移除
            tasks = await self._load_file(self.tasks_path)
            tasks = [t for t in tasks if t["id"] != task.id]
            await self._save_file(self.tasks_path, tasks)
