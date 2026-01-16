import os
import httpx
from bs4 import BeautifulSoup
from typing import Optional, List
from sidecar.domain.models import Task, TaskStatus, Source, DownloadMode
from sidecar.domain.repositories import IDownloader

class DMHYDownloader(IDownloader):
    def __init__(self, base_url: str = "https://share.dmhy.org"):
        self.base_url = base_url

    def get_source(self) -> Source:
        return Source.DMHY

    async def download(self, task: Task) -> bool:
        """從 DMHY 搜尋並下載"""
        if not task.metadata or not task.metadata.song_title:
            task.update_status(TaskStatus.FAILED, error="缺少元數據，無法搜尋下載")
            return False

        search_query = f"{task.metadata.anime_title} {task.metadata.song_title}"
        task.update_status(TaskStatus.DOWNLOADING, progress=10.0)

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # 1. 搜尋
                search_url = f"{self.base_url}/topics/list"
                params = {"keyword": search_query}
                response = await client.get(search_url, params=params)
                response.raise_for_status()

                # 2. 解析 HTML 獲取第一個結果
                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("#topic_list tbody tr")
                if not rows:
                    task.update_status(TaskStatus.FAILED, error="找不到符合的資源")
                    return False

                # 取得第一個有效的資源行
                first_row = rows[0]
                title_link = first_row.select_one(".title a")
                download_link = first_row.select_one("a.download-arrow") # 通常是種子下載頁面或直接連結

                if not title_link:
                    task.update_status(TaskStatus.FAILED, error="解析資源路徑失敗")
                    return False

                # 進入細節頁獲取磁力和種子檔連結
                detail_url = self.base_url + title_link['href']
                detail_resp = await client.get(detail_url)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

                # 獲取磁力連結
                magnet_link = detail_soup.select_one("#magnet")
                # 獲取種子檔連結
                torrent_link = detail_soup.select_one("#tabs-1 a[href$='.torrent']")

                if task.dmhy_mode == DownloadMode.TORRENT:
                    # 模式 B：僅下載種子檔案
                    if not torrent_link:
                         task.update_status(TaskStatus.FAILED, error="找不到種子檔案連結")
                         return False
                    
                    torrent_url = "https:" + torrent_link['href'] if torrent_link['href'].startswith("//") else torrent_link['href']
                    if not torrent_url.startswith("http"): torrent_url = self.base_url + torrent_url

                    os.makedirs(task.target_dir, exist_ok=True)
                    torrent_filename = os.path.basename(torrent_url)
                    save_path = os.path.join(task.target_dir, torrent_filename)

                    t_resp = await client.get(torrent_url)
                    t_resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        f.write(t_resp.content)
                    
                    task.update_status(TaskStatus.COMPLETED, progress=100.0)
                    return True

                else:
                    # 模式 A：進階下載影片 (目前先實作磁力連結獲取，留作未來整合 BitTorrent client)
                    # [TODO] 整合 libtorrent 或外部下載器介面
                    if not magnet_link:
                        task.update_status(TaskStatus.FAILED, error="找不到磁力連結")
                        return False
                    
                    # 由於直接下載影片需要 BT 客戶端邏輯，暫時將磁力連結寫入檔案作為替代方案
                    os.makedirs(task.target_dir, exist_ok=True)
                    with open(os.path.join(task.target_dir, "magnet.txt"), "w") as f:
                        f.write(magnet_link.get_text())

                    task.update_status(TaskStatus.FAILED, error="模式 A (直接下載影片) 尚未整合 BT 客戶端引擎，磁力連結已儲存至 magnet.txt")
                    return False

        except Exception as e:
            task.update_status(TaskStatus.FAILED, error=f"DMHY 錯誤: {str(e)}")
            return False
