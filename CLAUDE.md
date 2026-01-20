# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概覽

OpusED 是一款動畫主題曲 (OP/ED) 獲取工具，採用 Electron + Vue 3 + FastAPI 的雙進程架構。

### 技術架構

- **Frontend Process (Electron Main + Renderer)**
  - Electron 主進程：管理應用生命週期、Sidecar 進程、IPC 通訊、檔案系統操作
  - Vue 3 渲染進程：用戶介面、狀態管理 (Pinia)、路由 (Vue Router)
  - 負責：任務狀態管理、JSON 資料持久化、批次任務流程編排

- **Backend Process (Sidecar - FastAPI)**
  - Python FastAPI 服務，作為 Electron 的子進程運行
  - 負責：非同步爬蟲、元數據搜尋、下載調度
  - **無狀態設計**：不持久化系統狀態，所有狀態由 Electron 主進程管理
  - Port: 8000 (開發環境)

### 領域驅動設計 (DDD)

前端與後端均採用 DDD 三層架構：

1. **Domain Layer**: 核心實體與業務規則
   - Frontend: `src/shared/models.ts` (Task, Metadata, enums)
   - Backend: `sidecar/domain/models.py` (Task, Metadata, Source, TaskStatus)

2. **Application Layer**: 用例與業務邏輯組合
   - Frontend: `src/main/application/BatchManagementService.ts`
   - Backend: `sidecar/application/use_cases.py` (DownloadTaskUseCase, SearchMetadataUseCase)

3. **Infrastructure Layer**: 技術實作細節
   - Frontend: `src/main/infrastructure/TaskRepository.ts` (JSON 持久化)
   - Backend: `sidecar/infrastructure/` (爬蟲、下載器、元數據提供者)

## 開發環境設置

### 必要工具

- Node.js v18+ with pnpm (required: `pnpm@10.8.1`)
- Python 3.10+
- Git

### 初始化步驟

```bash
# 1. 設定 Python 虛擬環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安裝 Python 依賴（注意：目前沒有 requirements.txt，需手動安裝）
pip install fastapi uvicorn pydantic httpx beautifulsoup4 yt-dlp

# 3. 安裝前端依賴
pnpm install
```

## 常用指令

### 開發模式

```bash
# 啟動開發環境（同時啟動 Electron + Sidecar）
pnpm run dev

# 等同於
pnpm run start
```

開發模式行為：

- Electron 主進程會自動啟動 Sidecar (`.venv/bin/python -m uvicorn sidecar.app.main:app --port 8000 --reload`)
- Renderer 會開啟 DevTools
- 支援熱重載

### 構建

```bash
# 構建所有進程（main, preload, renderer）
pnpm run build

# 預覽構建結果
pnpm run preview
```

### 測試

```bash
# 執行 Python 測試
pytest

# 執行特定測試
pytest sidecar/tests/domain/test_models.py
pytest sidecar/tests/infrastructure/test_metadata_provider.py
```

### 程式碼格式化

```bash
# Python 程式碼格式化
black .

# TypeScript/Vue 格式化（如有配置 ESLint/Prettier）
# 目前專案未配置，需手動檢查
```

## 專案結構

```
opus-ed/
├── src/
│   ├── main/                    # Electron 主進程
│   │   ├── index.ts            # 入口、Sidecar 生命週期管理
│   │   ├── application/        # 應用層服務
│   │   │   └── BatchManagementService.ts
│   │   └── infrastructure/     # 基礎設施層
│   │       └── TaskRepository.ts (JSON 持久化)
│   ├── renderer/               # Vue 3 前端
│   │   └── src/
│   │       ├── views/          # 頁面組件
│   │       │   ├── Dashboard.vue
│   │       │   ├── BatchInput.vue
│   │       │   └── PreviewEdit.vue
│   │       ├── store/          # Pinia 狀態管理
│   │       │   ├── useTaskStore.ts
│   │       │   └── useSidecarStore.ts
│   │       └── router/         # Vue Router
│   ├── preload/                # Electron Preload (IPC Bridge)
│   │   └── index.ts
│   └── shared/                 # 共享型別與常數
│       ├── models.ts
│       └── constants.ts
├── sidecar/                    # Python FastAPI 服務
│   ├── domain/                 # 領域層
│   │   ├── models.py           # 實體定義
│   │   └── repositories.py     # 倉儲介面
│   ├── application/            # 應用層
│   │   └── use_cases.py
│   ├── infrastructure/         # 基礎設施層
│   │   ├── metadata_provider.py (Bangumi API)
│   │   ├── youtube_downloader.py (yt-dlp)
│   │   ├── dmhy_downloader.py (動漫花園爬蟲)
│   │   └── task_manager.py     # 內存任務管理
│   ├── app/
│   │   └── main.py             # FastAPI 路由定義
│   └── tests/                  # 測試
│       ├── domain/
│       └── infrastructure/
├── .venv/                      # Python 虛擬環境
└── out/                        # 構建輸出目錄
```

## 重要架構說明

### IPC 通訊架構

1. **Renderer → Main**: 透過 `window.api.*` (定義於 `src/preload/index.ts`)
2. **Main → Sidecar**: HTTP REST API (`http://127.0.0.1:8000`)
3. **IPC Channels**: 定義於 `src/shared/constants.ts` 的 `IPC_CHANNELS`

### 資料流

```
User Input (Vue)
  → window.api.createBatchTasks()
  → IPC Main Handler (src/main/index.ts)
  → BatchManagementService.createBatchTasks()
  → Sidecar API (GET /metadata/search, POST /download)
  → Infrastructure Layer (爬蟲/下載器)
  → TaskRepository (JSON 持久化)
  → State Update (Pinia Store)
  → UI Update
```

### Sidecar 生命週期管理

- **啟動**: `app.whenReady()` → `startSidecar()` (src/main/index.ts:17-59)
- **開發環境**: 使用 `.venv/bin/python` 執行 uvicorn，port 8000，啟用 reload
- **關閉**: `app.on('before-quit')` → `stopSidecar()` (src/main/index.ts:61-67)
- **生產環境**: 目前未實作（預留邏輯）

### 任務狀態管理

- **狀態機**: PENDING → DOWNLOADING → COMPLETED/FAILED
- **持久化**: Electron 主進程透過 TaskRepository 寫入 JSON
- **進度查詢**: Renderer 透過 Sidecar 的 `/tasks/{task_id}/status` 輪詢

### Python 依賴管理

注意：專案目前**沒有 requirements.txt**，必要依賴包括：

- fastapi
- uvicorn
- pydantic
- httpx (用於 HTTP 請求)
- beautifulsoup4 (用於網頁解析)
- yt-dlp (用於 YouTube 下載)

建議在開發前先確認虛擬環境已安裝這些依賴。

## 開發規範

### Spec-Driven Development (SDD)

任何功能實作前，必須先在 `implementation_plan.md` 中定義 Spec 並獲得確認。

### Test-Driven Development (TDD)

- 核心邏輯（Scraper, Parser, Domain Models）必須有對應測試
- 遵循紅燈/綠燈/重構循環
- 測試位置：`sidecar/tests/`

### DDD 分層規則

**Domain Layer 禁止導入外部框架庫**：

- ❌ 禁止：`import fastapi`, `import httpx`, `import axios`
- ✅ 允許：標準庫、dataclasses、typing、datetime

### Commit Message 規範

採用 Angular Convention：

```
<type>(<scope>): <subject>

type: feat, fix, refactor, docs, test, chore
scope: ui, core, api, infra, electron, docs, deps, config
```

範例：

```
feat(ui): 優化預覽頁面的自定義關鍵字輸入 UI
fix(core): 修正 Bangumi 元數據解析錯誤
refactor(infra): 改進下載進度輪詢機制
```

## 常見開發任務

### 新增下載源

1. 在 `sidecar/infrastructure/` 新增 downloader
2. 實作 `Downloader` 介面（參考 `youtube_downloader.py`）
3. 在 `sidecar/app/main.py` 註冊到 `downloaders` 列表
4. 更新 `src/shared/models.ts` 的 `Source` enum

### 修改任務狀態流程

1. 更新 `src/shared/models.ts` 的 `TaskStatus` enum
2. 同步更新 `sidecar/domain/models.py` 的 `TaskStatus`
3. 調整 `Task.update_status()` 邏輯
4. 更新相關 UI 組件（如 Dashboard.vue）

### 新增 API 端點

1. 在 `sidecar/app/main.py` 定義路由
2. 實作對應的 Use Case（`sidecar/application/use_cases.py`）
3. 在 `src/main/application/BatchManagementService.ts` 新增呼叫方法
4. 在 `src/preload/index.ts` 暴露 API 給 Renderer
5. 更新 `src/shared/constants.ts` 新增 IPC_CHANNEL（如需要）

## 除錯技巧

### Electron DevTools

開發模式下自動開啟 DevTools，可檢查 Renderer 進程的狀態與網路請求。

### Electron Main Process 除錯

根據 `src/main/index.ts:102-104`，開發模式已啟用 remote debugging：

```typescript
app.commandLine.appendSwitch("remote-debugging-port", "9222");
```

可在 Chrome 開啟 `chrome://inspect` 連接 Electron 主進程。

### Sidecar 日誌

- Sidecar stdout/stderr 會轉發到 Electron 主進程 console
- 查看 terminal 輸出的 `[Sidecar]:` 前綴日誌
- FastAPI 的 uvicorn 日誌會顯示 API 請求

### Python 測試除錯

```bash
# 顯示詳細輸出
pytest -v

# 顯示 print 語句
pytest -s

# 只執行特定測試
pytest sidecar/tests/domain/test_models.py::TestTask::test_update_status
```

## 設定檔說明

- `electron.vite.config.ts`: Vite 建置設定，定義 alias (`@main`, `@shared`, `@renderer`)
- `tailwind.config.js`: Tailwind CSS 設定
- `tsconfig.json`: TypeScript 根設定
- `src/renderer/tsconfig.json`: Renderer 進程專用 TypeScript 設定
- `package.json`: pnpm 依賴管理，必須使用 `pnpm@10.8.1`

## 其他注意事項

### 路徑別名

在 TypeScript 中可使用以下別名：

- `@main/*` → `src/main/*`
- `@shared/*` → `src/shared/*`
- `@renderer/*` → `src/renderer/src/*`
- `@infrastructure/*` → `src/main/infrastructure/*`

### 無狀態 Sidecar 設計

Sidecar 不應持久化任何系統狀態。所有狀態管理（任務列表、歷史紀錄）由 Electron 主進程的 TaskRepository 負責。Sidecar 只負責執行下載任務與元數據搜尋。

### 未來 SaaS 化考量

專案設計考慮未來 SaaS 化：

- Frontend 作為 Orchestrator，可替換為 Web 前端
- Sidecar 作為無狀態 Service，易於水平擴展
- JSON 持久化可遷移至資料庫

## Technology Stack

This project uses:

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Typed superset of JavaScript
- **Python** - Backend/scripting language

## Use Context7 MCP for Loading Documentation

Context7 MCP is available to fetch up-to-date documentation with code examples.

**Recommended library IDs**:

- `vue` - Vue.js 3 official documentation with composition API, reactivity system, and component patterns
- `typescript` - TypeScript language reference, type system, and compiler options
- `python` - Python standard library and language reference
- `pydantic` - Python data validation using type hints (if using Pydantic)
- `fastapi` - Modern Python web framework (if building APIs)
- `axios` - Promise-based HTTP client for browser and Node.js
- `vite` - Next generation frontend build tool
- `pinia` - Vue store library (if using state management)

### How to Use

When you need documentation for these technologies, the Context7 MCP server can fetch current documentation with examples. Simply reference the library ID when asking questions about implementation patterns or API usage.

## Use gemini cli for code search

- 你可以使用 gemini cli 來呼叫 gemini cli 這個工具做事情， gemini cli 的上下文 token 很大，請你用它找專案裡的程式碼，上網查資料等。但禁止使用它修改或刪除檔案。這是一個使用範例 `Bash(gemini -p "找出專案裡使用 xAI 的地方")`
- 你可以多開 gemini cli session 來平行運作，以免等待回應太久而耽誤了工作。

## Use Serena MCP for Semantic Code Analysis instead of regular code search and editing

Serena MCP is available for advanced code retrieval and editing capabilities.

**When to use Serena:**

- Symbol-based code navigation (find definitions, references, implementations)
- Precise code manipulation in structured codebases
- Prefer symbol-based operations over file-based grep/sed when available

**Key tools:**

- `find_symbol` - Find symbol by name across the codebase
- `find_referencing_symbols` - Find all symbols that reference a given symbol
- `list_symbols` - List all symbols in a file or scope
- `get_symbol_source` - Get the source code of a specific symbol

**Usage notes:**

- Memory files can be manually reviewed/edited in `.serena/memories/`

## Use Codemap CLI for Codebase Navigation

Codemap CLI is available for intelligent codebase visualization and navigation.

**Required Usage** - You MUST use `codemap --diff --ref master` to research changes different from default branch, and `git diff` + `git status` to research current working state.

### Quick Start

```bash
codemap .                    # Project tree
codemap --only vue,ts,py .   # Just Vue, TypeScript, Python files
codemap --exclude .xcassets,Fonts,.png .  # Hide assets
codemap --depth 2 .          # Limit depth
codemap --diff --ref master  # What changed vs master
codemap --deps .             # Dependency flow
```

### Options

| Flag                   | Description                             |
| ---------------------- | --------------------------------------- |
| `--depth, -d <n>`      | Limit tree depth (0 = unlimited)        |
| `--only <exts>`        | Only show files with these extensions   |
| `--exclude <patterns>` | Exclude files matching patterns         |
| `--diff`               | Show files changed vs main branch       |
| `--ref <branch>`       | Branch to compare against (with --diff) |
| `--deps`               | Dependency flow mode                    |
| `--importers <file>`   | Check who imports a file                |
| `--skyline`            | City skyline visualization              |
| `--json`               | Output JSON                             |

**Smart pattern matching** - no quotes needed:

- `.png` - any `.png` file
- `Fonts` - any `/Fonts/` directory
- `*Test*` - glob pattern

### Diff Mode

See what you're working on:

```bash
codemap --diff --ref master
codemap --diff --ref dev
codemap --diff --ref v2
```
