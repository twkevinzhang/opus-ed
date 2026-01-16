import { app, shell, BrowserWindow, ipcMain } from "electron";
import { join } from "path";
import { electronApp, optimizer, is } from "@electron-toolkit/utils";

import { IPC_CHANNELS } from "../shared/constants";
import { TaskRepository } from "./infrastructure/TaskRepository";
import { BatchManagementService } from "./application/BatchManagementService";

// 初始化基礎設施與服務
const taskRepo = new TaskRepository();
const batchService = new BatchManagementService(taskRepo);

function createWindow(): void {
  // 建立瀏覽器視窗
  const mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    webPreferences: {
      preload: join(__dirname, "../preload/index.mjs"),
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
        token
      );
    }
  );

  ipcMain.handle(IPC_CHANNELS.START_DOWNLOAD, async (_, taskId) => {
    return await batchService.startDownload(taskId);
  });

  ipcMain.handle(IPC_CHANNELS.DELETE_TASK, async (_, taskId) => {
    return await taskRepo.deleteTask(taskId);
  });
}
