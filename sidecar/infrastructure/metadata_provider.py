import httpx
import logging
import urllib.parse
from typing import List, Optional, Dict, Any
from sidecar.domain.models import Metadata
from sidecar.domain.repositories import IMetadataProvider

logger = logging.getLogger(__name__)

class BangumiMetadataProvider(IMetadataProvider):
    def __init__(self, base_url: str = "https://api.bgm.tv"):
        self.base_url = base_url

    async def get_metadata(self, anime_title: str, token: Optional[str] = None) -> List[Metadata]:
        """
        搜尋動畫並獲取其角色、曲目資訊 (使用 /v0/episodes API)。
        """
        headers = {
            "User-Agent": "twkevinzhang/OpusED (https://github.com/twkevinzhang/OpusED)",
            "Accept": "application/json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True) as client:
            try:
                # 1. 搜尋條目 (使用 URL 編碼)
                encoded_title = urllib.parse.quote(anime_title)
                search_url = f"{self.base_url}/search/subject/{encoded_title}"
                params = {"type": 2}  # 2 為動畫
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if not data.get("list"):
                    logger.warning(f"Bangumi 找不到動畫: {anime_title}")
                    return []
                
                # 取第一個結果的 ID
                subject_id = data["list"][0]["id"]
                anime_name_cn = data["list"][0].get("name_cn") or data["list"][0].get("name")
                logger.info(f"Found Subject: {anime_name_cn} ({subject_id})")

                results = []

                # 2. 獲取 OP (type=2) 和 ED (type=3)
                # API: /v0/episodes?subject_id={id}&type={type}
                ep_types = {2: "OP", 3: "ED"}
                
                for ep_type_id, type_label in ep_types.items():
                    ep_url = f"{self.base_url}/v0/episodes"
                    ep_params = {"subject_id": subject_id, "type": ep_type_id}
                    
                    ep_resp = await client.get(ep_url, params=ep_params)
                    ep_resp.raise_for_status()
                    ep_data = ep_resp.json()
                    
                    ep_list = ep_data.get("data", [])
                    for ep in ep_list:
                        song_title = ep.get("name")
                        desc = ep.get("desc", "")
                        artist = self._parse_artist_from_desc(song_title, desc)
                        
                        if song_title:
                            results.append(Metadata(
                                anime_title=anime_name_cn,
                                song_title=song_title,
                                artist=artist,
                                type=type_label,
                                bangumi_id=str(subject_id)
                            ))

                if not results:
                     logger.warning(f"No OP/ED found for {anime_name_cn}")
                     # Fallback empty result
                     results.append(Metadata(
                        anime_title=anime_name_cn,
                        song_title="[請輸入歌曲]",
                        artist="[請輸入歌手]",
                        type="OP/ED",
                        bangumi_id=str(subject_id)
                    ))

                return results

            except Exception as e:
                logger.error(f"Bangumi 獲取元數據失敗: {e}")
                return []

    def _parse_artist_from_desc(self, song_title: str, desc: str) -> str:
        """
        從 Episode 描述中解析歌手。
        策略：
        1. 尋找包含歌名的行 (可能是「歌名」或 "歌名")。
        2. 取其下一行作為歌手。
        3. 如果找不到歌名，嘗試尋找常見的歌手標籤行。
        """
        if not desc:
            return "未知歌手"
            
        lines = [line.strip() for line in desc.splitlines() if line.strip()]
        
        # 嘗試尋找歌名所在行
        title_index = -1
        for i, line in enumerate(lines):
            # 寬鬆匹配歌名 (忽略可能的引號)
            if song_title in line:
                title_index = i
                break
        
        if title_index != -1 and title_index + 1 < len(lines):
            # 歌名的下一行通常是歌手
            artist_line = lines[title_index + 1]
            # 過濾掉可能的標籤，例如 "作詞..."
            if not any(keyword in artist_line for keyword in ["作詞", "作曲", "編曲"]):
                return artist_line

        # 備用策略：尋找 "歌手" 關鍵字
        for line in lines:
            if line.startswith("歌手") or line.startswith("Artist"):
                 parts = line.split("：", 1) if "：" in line else line.split(":", 1)
                 if len(parts) > 1:
                     return parts[1].strip()
        
        # 簡單取非標籤行 (非常粗略)
        # 通常前幾行是 title -> song -> artist
        # 如果找不到明確結構，暫時回傳未知
        return "未知歌手"
