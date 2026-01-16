import { contextBridge } from "electron";
import { exposeElectronAPI } from "@electron-toolkit/preload";

// 為渲染進程暴露客製化 API
const api = {};

// 只有在啟用上下文隔離的情況下才使用 `contextBridge` API，
// 否則直接掛載到全域 window 物件
if (process.contextIsolated) {
  try {
    exposeElectronAPI();
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  // @ts-ignore (define in d.ts)
  window.electron = electronAPI;
  // @ts-ignore (define in d.ts)
  window.api = api;
}
