/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

interface Window {
  electron: import("@electron-toolkit/preload").ElectronAPI;
  api: {
    getTasks: () => Promise<import("../../shared/models").Task[]>;
    getHistory: () => Promise<import("../../shared/models").Task[]>;
    createBatchTasks: (data: {
      titles: string[];
      targetDir: string;
      source: string;
      dmhyMode: string;
      token?: string;
    }) => Promise<import("../../shared/models").Task[]>;
    startDownload: (taskId: string) => Promise<void>;
    deleteTask: (taskId: string) => Promise<void>;
  };
}
