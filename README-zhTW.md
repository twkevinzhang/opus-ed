# OpusED

OpusED 是一款現代化的動畫主題曲 (OP/ED) 獲取工具，旨在幫助動漫愛好者輕鬆蒐集、管理與下載喜愛的歌曲。

[English Version (README.md)](README.md)

## 📥 下載與安裝

對於一般使用者，請前往 **[Releases 頁面](https://github.com/twkevinzhang/opus-ed/releases)** 下載適用於您作業系統的最新安裝檔。

---

## 🚀 使用教學

### 1. 儀表板概覽

啟動應用程式後，您會看到簡潔的儀表板，顯示目前的任務狀態與 Sidecar 服務連接情形。
![儀表板](docs/dashboard.png)

### 2. 批次任務初始化

在輸入框中輸入動畫標題（一行一個）。選擇下載來源（YouTube 或動漫花園）並設定下載路徑。

> [!TIP]
> 下載路徑現在預設指向您系統中的「下載 (Downloads)」資料夾，無需重複選擇！

![批次初始化](docs/batch-input.png)

### 3. 元數據預覽與編輯

在正式開始下載前，您可以預覽搜尋結果並編輯歌曲資訊，確保下載後的檔案資訊（Metadata）正確無誤。
![預覽與編輯](docs/preview-edit.png)

---

## ✨ 核心特色

- **批次處理**：一次搜尋多個動畫，自動匹配對應曲目。
- **多來源支援**：整合 YouTube (透過 yt-dlp) 與動漫花園 (DMHY) 搜尋引擎。
- **極致視覺體驗**：基於 Electron + Vue 3 的現代化 UI，支援動態特效與深色模式。
- **智慧化預設**：自動獲取系統下載路徑，簡化操作流程。

## 🛠️ 開發者指南

如果您想參與開發或自行建置：

- **[DEVELOPMENT.md](DEVELOPMENT.md)**：開發環境建置與啟動流程。
- **[CONTRIBUTING.md](CONTRIBUTING.md)**：貢獻規範、程式碼風格與 Git 提交標準。

---

_專為動漫愛好者打造的歌曲收藏利器。_
