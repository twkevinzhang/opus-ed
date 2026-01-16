# OpusED 需求分析與功能規格 (Final)

本文件定義了 `OpusED` 的核心功能規格，作為開發階段的真理之源。

## 1. 專案目標

現代化動畫主題曲 (OP/ED) 獲取工具，支援多來源 (YouTube/DMHY) 與批次處理流程。具備無狀態設計，預留未來擴展為 SaaS 服務的可行性。

## 2. 核心功能與工作流

### 2.1 批次任務初始化 (Batch Process)

- **多行輸入**：輸入動畫標題（一行一個）。
- **進階參數 (每趟執行)**：
  - **Bangumi.moe Token**：用於獲取歌曲元數據。
  - **下載資料夾**。
  - **優先影片來源** (YouTube 或 DMHY)。
  - **DMHY 模式選擇**：[預設進階] 直接下載影片 或 [簡易] 僅下載 .torrent 檔案。

### 2.2 預覽與編輯 (Preview & Edit)

- **資訊校對**：顯示從 Bangumi 獲取的歌曲名稱、歌手與搜尋結果預覽。
- **單筆編輯**：可手動修改單筆任務的搜尋關鍵字、切換來源、或個別下載路徑。
- **核准排程**：確認後寫入 `tasks.json` 並啟動 Sidecar 下載進程。

### 2.3 執行下載 (Download Execution)

- **YouTube Downloader**：使用 `yt-dlp` 進行影像/音訊提取。
- **DMHY Downloader**：
  - **模式 A (影片)**：整合協定直接下載影片檔案。
  - **模式 B (種子)**：僅將 `.torrent` 檔案存入目標目錄。
- **紀錄儲存**：完成後更新 `download_history.json`。

## 3. 技術設計 (Sidecar)

### 3.1 無狀態架構 (Stateless)

- **請求驅動**：所有敏感資訊 (Token, Paths) 在 API 調用時傳遞，不儲存於 Python 全域變數。
- **DDD 架構**：
  - `Domain`：定義 `Task`、`Source` 與 `DownloadMode`。
  - `Application`：處理從 Bangumi 獲取內容並分發任務。
  - `Infrastructure`：實作 `yt-dlp` 下載器與 DMHY 爬蟲/下載器。

### 3.2 持久化

- 使用 JSON 格式存儲於 `sidecar/data/`。
- `tasks.json`：追蹤目前工作進度。
- `download_history.json`：歷史已完成紀錄。

## 4. 驗證計劃

- **TDD**：確保 Bangumi 元數據解析與 DMHY 搜尋邏輯的正確性。
- **模式切換測試**：驗證 DMHY 在「影片」與「種子」模式下的產出是否符合預期。
