"""
TaskManager: 在内存中管理所有活跃任务状态的单例类。

此模块属于 Infrastructure 层，负责任务状态的运行时管理。
"""

from typing import Optional
from sidecar.domain.models import Task


class TaskManager:
    """
    单例模式：在内存中管理所有活跃任务状态。

    Sidecar 是无状态服务，但下载任务需要在执行期间追踪进度。
    TaskManager 提供任务的临时存储，供 API 端点查询进度。
    """
    _instance: Optional["TaskManager"] = None
    _tasks: dict[str, Task]

    def __new__(cls) -> "TaskManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "TaskManager":
        """获取 TaskManager 单例实例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例（仅用于测试）。"""
        cls._instance = None

    def add_task(self, task: Task) -> None:
        """添加任务到管理器。"""
        self._tasks[task.id] = task

    def get_task(self, task_id: str) -> Optional[Task]:
        """根据 ID 获取任务。"""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """获取所有活跃任务。"""
        return list(self._tasks.values())

    def remove_task(self, task_id: str) -> bool:
        """移除任务。返回是否成功移除。"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def clear_all(self) -> None:
        """清空所有任务（仅用于测试）。"""
        self._tasks.clear()
