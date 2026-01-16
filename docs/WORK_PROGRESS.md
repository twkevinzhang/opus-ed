# OpusED 開發進度追蹤 (WORK_PROGRESS)

此文件用於協助 AI Agents 快速理解專案當前狀態與上下文，減少 Token 消耗。

## 📅 最新狀態

- **日期**: 2026-01-16
- **當前階段**: 階段 4 - 整合驗證
- **最近里程碑**: 完成功能視圖實作 (Batch Input, Preview, Dashboard)

## 🚀 功能開發矩陣

| 功能模組         | 前端 (Vue 3) | 後端 (Sidecar) | 整合狀態  | 備註                               |
| :--------------- | :----------: | :------------: | :-------: | :--------------------------------- |
| **專案架構**     |   ✅ 完成    |    ✅ 完成     | ✅ 已對接 | IPC Bridge 與 Stateless API 運作中 |
| **批次輸入**     |   ✅ 完成    |    ✅ 完成     | ✅ 已對接 | 支援多行標題與 Token               |
| **Bangumi 整合** |     N/A      |    ✅ 完成     | ✅ 已對接 | 前端可校對 Infobox 資訊            |
| **預覽/編輯**    |   ✅ 完成    |    ✅ 完成     | ✅ 已對接 | 支援自定義關鍵字                   |
| **YT 下載**      |     N/A      |    ✅ 完成     | ✅ 已對接 | 狀態輪詢完成                       |
| **DMHY 下載**    |     N/A      |    ✅ 完成     | ✅ 已對接 | 支援 影片/種子 雙模式              |
| **任務持久化**   |   ✅ 完成    |      N/A       | ✅ 已對接 | Electron 側 JSON 存儲              |

## 🏗️ 技術債與注意事項

1. **Sidecar API**: 目前 Sidecar 尚未提供標準 REST API，需優先定義 OpenAPI Spec。
2. **IPC 通訊**: 前端目前僅有 HTTP Client 雛形，需封裝與 Sidecar 的通訊層。
3. **MCP 除錯**: 已配置 `remote-debugging-port: 9222`，開發時可多加利用。

## 📂 關鍵文件索引

- 規格說明: [docs/implementation_plan.md](docs/implementation_plan.md)
- 開發指南: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- 架構定義: [src/main/index.ts](src/main/index.ts) (Electron Main)
