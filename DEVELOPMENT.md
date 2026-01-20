# Development Guide

這份指南將引導你如何開發、構建並運行 OpusED。

## 📋 目錄

- [快速上手 (5 分鐘)](#quick-start)
- [架構概覽 (DDD)](#architecture)
- [專案結構](#structure)
- [開發工作流 (SDD & TDD)](#workflow)
- [常用指令](#commands)

---

## 🚀 快速上手 (5 分鐘) {#quick-start}

### 必備條件

- **Node.js**: 建議使用 v18+ (配合 **pnpm**)
- **Python**: 3.10+ (建議使用官方安裝程式)
- **Git**

### 安裝與啟動

```bash
# 1. 克隆儲存庫
git clone https://github.com/twkevinzhang/opus-ed.git
cd opus-ed

# 2. 設定 Python 環境 (venv)
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -r requirements.txt

# 3. 安裝前端依賴
pnpm install

# 4. 啟動開發模式
pnpm run dev
```

---

## 🏗️ 架構概覽 (DDD) {#architecture}

- **Frontend (Orchestrator)**: Electron + Vue 3。負責導航、任務狀態管理、以及 **JSON 資料持久化**。
- **Sidecar (Service)**: FastAPI (Python)。純粹的執行層，負責非同步爬蟲與下載任務，**不存儲系統狀態**。
- **DDD 分層 (前端與後端分別實作)**:
  - **Domain**: 定義核心實體 (Task, Metadata)。
  - **Application**: 前端處理批次管理與流程；後端處理搜尋與下載調度。
  - **Infrastructure**: 前端處理 IPC 與檔案 IO；後端實作爬蟲工具 (yt-dlp, BeautifulSoup)。

---

## 📁 專案結構 {#structure}

```text
opus-ed/
├── src/
│   ├── main/           # Electron 主進程
│   ├── renderer/       # Vue 3 前端程式碼
│   └── preload/        # Bridge 層
├── sidecar/
│   ├── domain/        # 核心實體與倉儲介面 (DDD)
│   ├── application/   # 業務邏輯組合 (DDD)
│   ├── infrastructure/# 技術細節實作 (DDD)
│   ├── app/           # FastAPI 路由定義
│   └── data/          # JSON 持久化檔案
├── .venv/              # 虛擬環境
├── package.json        # pnpm 設定
└── README.md
```

---

## 🔄 開發工作流 (SDD & TDD) {#workflow}

### 1. Spec-Driven Development (SDD)

任何功能實作前，**必須**先在 `implementation_plan.md` 中定義 Spec 並獲得承認。

### 2. Test-Driven Development (TDD)

優先撰寫 `sidecar/domain` 的單元測試：

```bash
# 執行測試
pytest
```

---

## 📦 常用指令 {#commands}

| 指令           | 描述                      |
| -------------- | ------------------------- |
| `pnpm run dev` | 啟動開發環境 (含 Sidecar) |
| `pytest`       | 執行所有 Python 邏輯測試  |
| `black .`      | 格式化 Python 程式碼      |

---

**Happy coding! 🚀**
