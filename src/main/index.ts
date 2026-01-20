import { app, shell, BrowserWindow, ipcMain, dialog } from "electron";
import { join } from "path";
import { electronApp, optimizer, is } from "@electron-toolkit/utils";
import { spawn, ChildProcess } from "child_process";

import { IPC_CHANNELS } from "../shared/constants";
import { TaskRepository } from "./infrastructure/TaskRepository";
import { BatchManagementService } from "./application/BatchManagementService";

// 初始化基礎設施與服務
const taskRepo = new TaskRepository();
const batchService = new BatchManagementService(taskRepo);

let pythonProcess: ChildProcess | null = null;
let mainWindow: BrowserWindow;

function startSidecar() {
  const isDev = is.dev;
  let pythonExecutable = "python";
  let args: string[] = [];

  if (isDev) {
    // 開發環境：使用 .venv 中的 python
    pythonExecutable = join(process.cwd(), ".venv/bin/python");
    args = [
      "-m",
      "uvicorn",
      "sidecar.app.main:app",
      "--port",
      "8000",
      "--reload",
    ];
  } else {
    // 生產環境：預留邏輯，暫時不實作
    console.log("Production sidecar not implemented yet.");
    return;
  }

  console.log(`Starting Sidecar: ${pythonExecutable} ${args.join(" ")}`);

  pythonProcess = spawn(pythonExecutable, args, {
    cwd: process.cwd(),
    shell: false,
    // 注意：shell: true 可能會導致信號傳遞問題，這裡先設為 false
    // 開發環境下 cwd 設為專案根目錄，以便 uvicorn 能找到 sidecar package
  });

  pythonProcess.stdout?.on("data", (data) => {
    console.log(`[Sidecar]: ${data}`);
  });

  pythonProcess.stderr?.on("data", (data) => {
    console.error(`[Sidecar Error]: ${data}`);
  });

  pythonProcess.on("close", (code) => {
    console.log(`Sidecar process exited with code ${code}`);
  });
}

function stopSidecar() {
  if (pythonProcess) {
    console.log("Stopping Sidecar...");
    pythonProcess.kill();
    pythonProcess = null;
  }
}

function createWindow(): void {
  // 建立瀏覽器視窗
  mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      sandbox: false,
    },
  });

  mainWindow.on("ready-to-show", () => {
    mainWindow.show();
  });

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: "deny" };
  });

  // 基於 electron-vite 的開發伺服器 HMR 或生產環境的靜態 HTML 載入
  if (is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    mainWindow.loadURL(process.env["ELECTRON_RENDERER_URL"]);
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
  }
}

// 根據 https://icodex.me/electron-devtools-mcp/ 配置除錯埠
// 必須在 app 準備好之前執行
if (is.dev) {
  app.commandLine.appendSwitch("remote-debugging-port", "9222");
}

app.whenReady().then(() => {
  // 為 64 位元系統設定應用程式使用者模型 ID
  electronApp.setAppUserModelId("com.electron");

  // 在開發環境中預設透過 F12 開啟或關閉 DevTools
  // 並忽略視窗建立時的 Command+R 重新整理
  app.on("browser-window-created", (_, window) => {
    optimizer.watchWindowShortcuts(window);
  });

  startSidecar(); // 啟動 Sidecar
  createWindow();
  setupIpc();

  app.on("activate", function () {
    // 在 macOS 上，當點擊 dock 圖示且沒有其他視窗開啟時，通常會重新建立一個視窗
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// 當所有視窗都關閉時退出，除了在 macOS 上
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  stopSidecar(); // 確保退出時關閉 Sidecar
});

function setupIpc(): void {
  ipcMain.handle(IPC_CHANNELS.GET_ALL_TASKS, async () => {
    return await taskRepo.getAllTasks();
  });

  ipcMain.handle(IPC_CHANNELS.GET_HISTORY, async () => {
    return await taskRepo.getHistory();
  });

  ipcMain.handle(
    IPC_CHANNELS.CREATE_BATCH_TASKS,
    async (_, { titles, targetDir, source, dmhyMode, token }) => {
      return await batchService.createBatchTasks(
        titles,
        targetDir,
        source,
        dmhyMode,
        token,
      );
    },
  );

  ipcMain.handle(IPC_CHANNELS.START_DOWNLOAD, async (_, taskId) => {
    return await batchService.startDownload(taskId);
  });

  ipcMain.handle(IPC_CHANNELS.DELETE_TASK, async (_, taskId) => {
    return await taskRepo.deleteTask(taskId);
  });

  ipcMain.handle(IPC_CHANNELS.SELECT_DIRECTORY, async () => {
    const result = await dialog.showOpenDialog({
      properties: ["openDirectory", "createDirectory"],
      title: "選擇下載目錄",
    });

    if (result.canceled) {
      return null;
    }

    return result.filePaths[0];
  });
  ipcMain.handle(IPC_CHANNELS.GET_DOWNLOAD_PATH, async () => {
    return app.getPath("downloads");
  });
}
