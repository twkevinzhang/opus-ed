import { defineStore } from "pinia";

export type SidecarStatus = "healthy" | "unhealthy" | "checking";

export const useSidecarStore = defineStore("sidecar", {
  state: () => ({
    status: "checking" as SidecarStatus,
    lastChecked: null as Date | null,
    checkInterval: null as number | null,
  }),

  getters: {
    statusText(): string {
      switch (this.status) {
        case "healthy":
          return "運行中";
        case "unhealthy":
          return "離線";
        case "checking":
          return "檢查中...";
      }
    },
    statusColor(): string {
      switch (this.status) {
        case "healthy":
          return "text-emerald-500";
        case "unhealthy":
          return "text-red-500";
        case "checking":
          return "text-yellow-500";
      }
    },
  },

  actions: {
    async checkHealth() {
      try {
        const response = await fetch("http://127.0.0.1:8000/health", {
          method: "GET",
          signal: AbortSignal.timeout(3000), // 3秒超時
        });

        if (response.ok) {
          const data = await response.json();
          this.status = data.status === "healthy" ? "healthy" : "unhealthy";
        } else {
          this.status = "unhealthy";
        }
      } catch (error) {
        console.error("Sidecar 健康檢查失敗:", error);
        this.status = "unhealthy";
      } finally {
        this.lastChecked = new Date();
      }
    },

    startHealthCheck(intervalMs: number = 10000) {
      // 立即執行一次檢查
      this.checkHealth();

      // 設定定期檢查（預設 10 秒）
      if (this.checkInterval) {
        clearInterval(this.checkInterval);
      }

      this.checkInterval = window.setInterval(() => {
        this.checkHealth();
      }, intervalMs);
    },

    stopHealthCheck() {
      if (this.checkInterval) {
        clearInterval(this.checkInterval);
        this.checkInterval = null;
      }
    },
  },
});
