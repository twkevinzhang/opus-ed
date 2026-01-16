import pytest
import httpx
from sidecar.infrastructure.metadata_provider import BangumiMetadataProvider

@pytest.mark.asyncio
async def test_bangumi_provider_search(respx_mock):
    # Mock Bangumi Search API
    search_route = respx_mock.get("https://api.bgm.tv/search/subject/Lycoris Recoil").mock(
        return_value=httpx.Response(200, json={
            "list": [{"id": 345678, "name": "Lycoris Recoil"}]
        })
    )
    
    # Mock Subject API
    subject_route = respx_mock.get("https://api.bgm.tv/v0/subjects/345678").mock(
        return_value=httpx.Response(200, json={
            "id": 345678,
            "name": "Lycoris Recoil",
            "name_cn": "莉可麗絲"
        })
    )
    
    provider = BangumiMetadataProvider()
    results = await provider.get_metadata("Lycoris Recoil")
    
    assert len(results) > 0
    assert results[0].anime_title == "莉可麗絲"
    assert results[0].bangumi_id == "345678"
    assert search_route.called
    assert subject_route.called
