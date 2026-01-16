import os
import httpx
import logging
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
from sidecar.domain.models import Task, TaskStatus, Source, DownloadMode

logger = logging.getLogger(__name__)

class DMHYDownloader:
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
        if hasattr(task, 'custom_keywords') and task.custom_keywords:
            search_query = task.custom_keywords

        task.update_status(TaskStatus.DOWNLOADING, progress=5.0)

        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                # 1. 搜尋
                search_url = f"{self.base_url}/topics/list"
                params = {"keyword": search_query}
                response = await client.get(search_url, params=params)
                response.raise_for_status()

                # 2. 解析 HTML 獲取第一個結果
                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("#topic_list tbody tr")
                if not rows:
                    task.update_status(TaskStatus.FAILED, error=f"在 DMHY 找不到符合的資源: {search_query}")
                    return False

                # 取得第一個有效的資源行
                first_row = rows[0]
                title_link = first_row.select_one(".title a")
                if not title_link:
                    task.update_status(TaskStatus.FAILED, error="解析資源標題連結失敗")
                    return False

                # 進入細節頁獲取磁力和種子檔連結
                detail_url = self.base_url + title_link['href']
                detail_resp = await client.get(detail_url)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

                # 獲取磁力連結
                magnet_link_node = detail_soup.select_one("#magnet")
                magnet_link = magnet_link_node.get_text() if magnet_link_node else None
                
                # 獲取種子檔連結
                torrent_link_node = detail_soup.select_one("#tabs-1 a[href$='.torrent']")
                torrent_url = None
                if torrent_link_node:
                    rel_url = torrent_link_node['href']
                    if rel_url.startswith("//"):
                        torrent_url = "https:" + rel_url
                    elif rel_url.startswith("/"):
                        torrent_url = self.base_url + rel_url
                    else:
                        torrent_url = rel_url

                if task.dmhy_mode == DownloadMode.TORRENT:
                    # 模式 B：僅下載種子檔案
                    if not torrent_url:
                         task.update_status(TaskStatus.FAILED, error="找不到可用於下載的種子檔案連結")
                         return False
                    
                    os.makedirs(task.target_dir, exist_ok=True)
                    torrent_filename = os.path.basename(torrent_url.split('?')[0])
                    if not torrent_filename.endswith(".torrent"):
                        torrent_filename += ".torrent"
                    
                    save_path = os.path.join(task.target_dir, torrent_filename)

                    t_resp = await client.get(torrent_url)
                    t_resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        f.write(t_resp.content)
                    
                    task.update_status(TaskStatus.COMPLETED, progress=100.0)
                    return True

                else:
                    # 模式 A：進階下載影片
                    if not magnet_link:
                        task.update_status(TaskStatus.FAILED, error="找不到可用於下載的磁力連結")
                        return False
                    
                    # 由於直接下載影片需要 BT 客戶端邏輯，暫時將磁力連結寫入檔案
                    os.makedirs(task.target_dir, exist_ok=True)
                    with open(os.path.join(task.target_dir, "magnet.txt"), "w") as f:
                        f.write(magnet_link)

                    # [NOTE] 未來這裡應整合 libtorrent 或外部下載程式
                    task.update_status(TaskStatus.FAILED, error="模式 A (直接下載影片) 尚未整合 BT 引擎，磁力連結已儲存至 magnet.txt。建議切換至 TORRENT 模式。")
                    return False

        except Exception as e:
            logger.error(f"DMHY 下載錯誤: {e}")
            task.update_status(TaskStatus.FAILED, error=f"DMHY 錯誤: {str(e)}")
            return False
