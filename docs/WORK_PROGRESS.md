# OpusED 開發進度追蹤 (WORK_PROGRESS)

此文件用於協助 AI Agents 快速理解專案當前狀態與上下文，減少 Token 消耗。

## 📅 最新狀態

- **日期**: 2026-01-16
- **當前階段**: 階段 2 - Frontend 基礎建設
- **最近里程碑**: 完成 Sidecar 核心重構與 API 強化

## 🚀 功能開發矩陣

| 功能模組         | 前端 (Vue 3) | 後端 (Sidecar) | 整合狀態  | 備註                              |
| :--------------- | :----------: | :------------: | :-------: | :-------------------------------- |
| **專案架構**     |   ✅ 完成    |    ✅ 完成     | ⏳ 待對接 | Electron/FastAPI DDD 架構整備完成 |
| **批次輸入**     |  ⬜ 待實作   |    ✅ 完成     |    ⬜     | 後端已支援 Batch API              |
| **Bangumi 整合** |     N/A      |    ✅ 完成     |    N/A    | 已實作 infobox 精確解析           |
| **預覽/編輯**    |  ⬜ 待實作   |    ✅ 完成     |    ⬜     | 後端已提供 Search API             |
| **YT 下載**      |     N/A      |    ✅ 完成     |    ⬜     | 優化完成 (yt-dlp)                 |
| **DMHY 下載**    |     N/A      |    ✅ 完成     |    ⬜     | 支援 影片/種子 雙模式             |
| **任務持久化**   |     N/A      |    ✅ 完成     |    ⬜     | 支援 custom_keywords              |

## 🏗️ 技術債與注意事項

1. **Sidecar API**: 目前 Sidecar 尚未提供標準 REST API，需優先定義 OpenAPI Spec。
2. **IPC 通訊**: 前端目前僅有 HTTP Client 雛形，需封裝與 Sidecar 的通訊層。
3. **MCP 除錯**: 已配置 `remote-debugging-port: 9222`，開發時可多加利用。

## 📂 關鍵文件索引

- 規格說明: [docs/implementation_plan.md](docs/implementation_plan.md)
- 開發指南: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- 架構定義: [src/main/index.ts](src/main/index.ts) (Electron Main)
