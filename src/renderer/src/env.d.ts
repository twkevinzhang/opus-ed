import { ElectronAPI } from "@electron-toolkit/preload";

interface SidecarAPI {
  getConfig: () => Promise<any>;
  checkSidecarHealth: () => Promise<{ success: boolean }>;
  storeSet: (key: string, val: any) => Promise<void>;
  storeGet: (key: string) => Promise<any>;
  getTasks: () => Promise<any>;
  getHistory: () => Promise<any>;
  createBatchTasks: (data: any) => Promise<any>;
  startDownload: (taskId: string) => Promise<any>;
  deleteTask: (taskId: string) => Promise<any>;
  getDownloadPath: () => Promise<string>;
  selectDirectory: () => Promise<string | null>;
}

declare global {
  interface Window {
    electron: ElectronAPI;
    api: SidecarAPI;
  }
}
