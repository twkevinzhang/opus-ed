import httpx
from typing import List, Optional
from sidecar.domain.models import Metadata
from sidecar.domain.repositories import IMetadataProvider

class BangumiMetadataProvider(IMetadataProvider):
    def __init__(self, base_url: str = "https://api.bgm.tv"):
        self.base_url = base_url

    async def get_metadata(self, anime_title: str, token: Optional[str] = None) -> List[Metadata]:
        """
        搜尋動畫並獲取其角色、曲目資訊。
        註：這裡目前先實作搜尋邏輯框架，具體 API 欄位對應需精細調整。
        """
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        headers["User-Agent"] = "twkevinzhang/OpusED (https://github.com/twkevinzhang/OpusED)"

        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            # 1. 搜尋條目
            search_url = f"{self.base_url}/search/subject/{anime_title}"
            params = {"type": 2}  # 2 為動畫
            response = await client.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("list"):
                return []
            
            # 取第一個結果的 ID
            subject_id = data["list"][0]["id"]
            
            # 2. 獲取章節/曲目資訊 (EPs)
            # 在 Bangumi 中，歌曲通常存在於 "crt" 或特定的 "ep" 描述中
            # 為了 Spec 準確性，我們這裡模擬返回格式，後續對接具體 EP 欄位
            subject_url = f"{self.base_url}/v0/subjects/{subject_id}"
            subject_resp = await client.get(subject_url)
            subject_resp.raise_for_status()
            subject_info = subject_resp.json()
            
            # 假設性邏輯：解析 subject_info 中的 OP/ED 字串
            # 實際開發中可能需要獲取 /subjects/{id}/characters 或解析 info_box
            results = []
            
            # 範例性回傳（待進一步解析 info_box）
            # 這裡先回傳一個包含搜尋到動畫名稱的 Placeholder，稍後在單元測試中 Mock
            results.append(Metadata(
                anime_title=subject_info.get("name_cn") or subject_info.get("name"),
                song_title="待解析歌曲",
                artist="待解析歌手",
                type="OP/ED",
                bangumi_id=str(subject_id)
            ))
            
            return results
