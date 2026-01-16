import { defineStore } from "pinia";
import { Task, Source, DownloadMode } from "../../../shared/models";

export const useTaskStore = defineStore("tasks", {
  state: () => ({
    tasks: [] as Task[],
    history: [] as Task[],
    isLoading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchTasks() {
      this.isLoading = true;
      try {
        this.tasks = await window.api.getTasks();
      } catch (err: any) {
        this.error = `獲取任務失敗: ${err.message}`;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchHistory() {
      try {
        this.history = await window.api.getHistory();
      } catch (err: any) {
        console.error("獲取歷史失敗:", err);
      }
    },

    async createBatch(data: {
      titles: string[];
      targetDir: string;
      source: Source;
      dmhyMode: DownloadMode;
      token?: string;
    }) {
      this.isLoading = true;
      try {
        const newTasks = await window.api.createBatchTasks(data);
        this.tasks.push(...newTasks);
      } catch (err: any) {
        this.error = `建立批次任務失敗: ${err.message}`;
      } finally {
        this.isLoading = false;
      }
    },

    async startDownload(taskId: string) {
      // 下載是異步執行的，我們僅發送請求
      try {
        await window.api.startDownload(taskId);
        // 實作上可考慮在此啟動定時輪詢或等待 IPC 事件更新狀態
      } catch (err: any) {
        this.error = `啟動下載失敗: ${err.message}`;
      }
    },

    async removeTask(taskId: string) {
      try {
        await window.api.deleteTask(taskId);
        this.tasks = this.tasks.filter((t) => t.id !== taskId);
      } catch (err: any) {
        console.error("刪除任務失敗:", err);
      }
    },
  },
});
