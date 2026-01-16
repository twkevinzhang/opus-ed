# AGENTS.md

本文件為 AI Agent 在 OpusED 儲存庫中工作時的「真理之源」。旨在提供高密度的專案上下文，最大化開發效率並減少 Token 消耗。

## 📚 重要文檔引用

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** - 貢獻與編碼規範 (**DDD**, **TDD**, Git Scopes)
2. **[docs/DEVELOPMENT.md](./DEVELOPMENT.md)** - 環境建置、啟動流程、目錄結構

---

## 專案概覽

OpusED 是一款現代化的動畫主題曲 (OP/ED) 管理與獲取工具。

### 核心技術棧

- **前端 (UI)**: Electron + Vue 3 (Vite + pnpm)
- **後端 (Sidecar)**: Python 3.10+ (FastAPI + asyncio + venv)
- **通訊**: REST API (localhost)
- **持久化**: JSON 檔案儲存

### 目錄結構與 DDD 映射

Sidecar 側嚴格遵守 **領域驅動設計 (Domain-Driven Design)**：

- `/sidecar/domain`: 核心業務邏輯、實體 (Entities)、值對象 (Value Objects)、倉儲介面 (Repository Interfaces)。**禁止依賴外部庫**。
- `/sidecar/application`: 用例 (Use Cases)、應用服務，協調領域層完成業務目標。
- `/sidecar/infrastructure`: 技術實作。包含 JSON 讀寫實作、FastAPI 啟動邏輯、爬蟲具體實作 (httpx/BS4)。
- `/src/main`: Electron 主進程 (System Interface)。
- `/src/renderer`: Vue 3 前端 (User Interface)。

---

## 🚀 開發哲學：Spec-Driven & TDD

### 1. Spec-Driven Development (SDD)

**所有重大開發前，必須執行以下流程：**

1. **需求確認**：與使用者反覆確認 Spec，確保不遺漏任何邊界條件。
2. **計畫編寫**：在執行前撰寫或更新 `implementation_plan.md` 並獲得批准。
3. **介面先行**：先定義 API 規格 或 Python 倉儲介面。

### 2. Test-Driven Development (TDD)

**開發過程中應優先考慮測試：**

- **紅燈**: 在實作邏輯前，先撰寫 `domain` 或 `use case` 的失敗測試。
- **綠燈**: 實作最簡邏輯使測試通過。
- **重構**: 在有測試保障的前提下優化程式碼品質。

---

## 🧘 AI Agent 自我審計協議 (Metacognitive Monitoring)

1. **反覆確認**: 若需求描述涉及業務邏輯變更，**必須**先向使用者詢問細節，不得盲目猜測。
2. **層級隔離**: 修改代碼時檢查是否破壞了 DDD 依賴原則（高層不應依賴低層）。
3. **非同步優先**: 所有 Python IO 必須為 `async`。
4. **Token 節約**: 優先使用 `diff` 或 `replace_file_content`。

---

## 任務檢查清單 (AI Checkpoint)

- [ ] 需求是否已與使用者對齊？(SDD)
- [ ] 測試是否已涵蓋核心邏輯？(TDD)
- [ ] 目錄與依賴是否符合 DDD 分層？
- [ ] Python 是否具備完整 Type Hints？

---

**Last Updated**: 2026-01-16
**Status**: DDD & TDD & SDD Integrated
