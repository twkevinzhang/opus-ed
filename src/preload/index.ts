import { contextBridge, ipcRenderer } from "electron";
import { electronAPI } from "@electron-toolkit/preload";
import { IPC_CHANNELS } from "../shared/constants";

// 自定義渲染進程 API
const api = {
  getTasks: () => ipcRenderer.invoke(IPC_CHANNELS.GET_ALL_TASKS),
  getHistory: () => ipcRenderer.invoke(IPC_CHANNELS.GET_HISTORY),
  createBatchTasks: (data: {
    titles: string[];
    targetDir: string;
    source: string;
    dmhyMode: string;
    token?: string;
  }) => ipcRenderer.invoke(IPC_CHANNELS.CREATE_BATCH_TASKS, data),
  startDownload: (taskId: string) =>
    ipcRenderer.invoke(IPC_CHANNELS.START_DOWNLOAD, taskId),
  deleteTask: (taskId: string) =>
    ipcRenderer.invoke(IPC_CHANNELS.DELETE_TASK, taskId),
};

// 使用 contextIsolation 曝露 API
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld("electron", electronAPI);
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  // @ts-ignore (用於無隔離環境)
  window.electron = electronAPI;
  // @ts-ignore
  window.api = api;
}
