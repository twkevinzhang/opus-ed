# Contributing to OpusED

感謝你考慮為 OpusED 做出貢獻！本文件定義了核心開發規範。

## 📋 目錄

- [Coding Standards (DDD & TDD)](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [PR Process](#pr-process)

---

## 編碼規範 (DDD & TDD) {#coding-standards}

### 1. 領域驅動設計 (DDD)

Sidecar 側應嚴格遵守三層架構：

- **Domain Layer**: 包含 Entity, Value Object, Repository 接口。
  - _規則_：嚴禁導入 `fastapi`, `httpx` 等邊界庫。
- **Application Layer**: 承接 API 請求並調用 Domain 完成任務。
- **Infrastructure Layer**: 實作 Repository 接口、JSON 讀寫、爬蟲細節。

### 2. 測試驅動開發 (TDD)

- **所有核心邏輯 (Scraper, Parser)** 都應具備對應的測試檔案。
- **紅燈/綠燈/重構** 循環是開發新 Feature 的標準配備。

### 3. 持久化政策 (JSON)

- 使用 **JSON** 格式。
- 資料存放於 `sidecar/data/`。
- 寫入必須考慮並發與完整性。

---

## Commit Message 規範 {#commit-message-guidelines}

採用 **Angular Convention**。

### Scope 清單

- `ui`: 前端 UI
- `core`: Python 核心 (Domain/Application)
- `api`: FastAPI/REST 介面
- `infra`: Infrastructure 實作
- `electron`: Electron 主進程
- `docs`: 文檔
- `deps`: 依賴
- `config`: 設定

---

**謝謝你讓 OpusED 變得更高品質！ 🚀**
