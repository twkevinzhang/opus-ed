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
        搜尋動畫並獲取其角色、曲目資訊。
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
                
                # 2. 獲取詳細資訊 (API v0)
                subject_url = f"{self.base_url}/v0/subjects/{subject_id}"
                subject_resp = await client.get(subject_url)
                subject_resp.raise_for_status()
                subject_info = subject_resp.json()
                
                results = []
                infobox = subject_info.get("infobox", [])
                
                # 嘗試從 infobox 中提取 OP/ED
                for item in infobox:
                    label = item.get("label", "")
                    value = item.get("value", "")
                    
                    # 匹配 OP, ED, 主題曲等標籤
                    metatype = None
                    if "OP" in label.upper() or "片頭" in label:
                        metatype = "OP"
                    elif "ED" in label.upper() or "片尾" in label:
                        metatype = "ED"
                    elif "主題" in label:
                        metatype = "Theme"
                    
                    if metatype and isinstance(value, str):
                        # 簡單解析：通常格式為 "歌名" 或 "歌名 / 歌手"
                        # 這裡做基礎處理，未來可增加更強的 regex
                        parts = value.split("/")
                        song_title = parts[0].strip().strip("「」『』\" ")
                        artist = parts[1].strip() if len(parts) > 1 else "未知歌手"
                        
                        results.append(Metadata(
                            anime_title=anime_name_cn,
                            song_title=song_title,
                            artist=artist,
                            type=metatype,
                            bangumi_id=str(subject_id)
                        ))
                    elif metatype and isinstance(value, list):
                        # 有時 value 是一個列表（多首 OP/ED）
                        for sub_item in value:
                            if isinstance(sub_item, dict) and "v" in sub_item:
                                v_str = sub_item["v"]
                                parts = v_str.split("/")
                                results.append(Metadata(
                                    anime_title=anime_name_cn,
                                    song_title=parts[0].strip().strip("「」『』\" "),
                                    artist=parts[1].strip() if len(parts) > 1 else "未知歌手",
                                    type=metatype,
                                    bangumi_id=str(subject_id)
                                ))

                # 如果 infobox 沒抓到，至少回傳一個基礎資訊供使用者手動輸入
                if not results:
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
