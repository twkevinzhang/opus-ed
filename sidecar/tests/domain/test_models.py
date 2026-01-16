import pytest
from sidecar.domain.models import Task, Metadata, TaskStatus, Source, DownloadMode

def test_task_initialization():
    task = Task(anime_title="Lycoris Recoil")
    assert task.status == TaskStatus.PENDING
    assert task.progress == 0.0
    assert task.anime_title == "Lycoris Recoil"
    assert task.id is not None

def test_task_status_update():
    task = Task(anime_title="Lycoris Recoil")
    task.update_status(TaskStatus.DOWNLOADING, progress=50.0)
    assert task.status == TaskStatus.DOWNLOADING
    assert task.progress == 50.0
    assert task.updated_at > task.created_at

def test_task_with_metadata():
    metadata = Metadata(
        anime_title="Lycoris Recoil",
        song_title="ALIVE",
        artist="ClariS",
        type="OP"
    )
    task = Task(anime_title="Lycoris Recoil", metadata=metadata)
    assert task.metadata.song_title == "ALIVE"
    assert task.metadata.artist == "ClariS"

def test_dmhy_task_modes():
    task_video = Task(source=Source.DMHY, dmhy_mode=DownloadMode.VIDEO)
    task_torrent = Task(source=Source.DMHY, dmhy_mode=DownloadMode.TORRENT)
    assert task_video.dmhy_mode == DownloadMode.VIDEO
    assert task_torrent.dmhy_mode == DownloadMode.TORRENT
