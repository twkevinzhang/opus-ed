<script setup lang="ts">
import { onMounted, onUnmounted, computed } from "vue";
import { useTaskStore } from "../store/useTaskStore";

const taskStore = useTaskStore();
const tasks = computed(() => taskStore.tasks);

let pollTimer: any = null;

onMounted(() => {
  taskStore.fetchTasks();
  // 每 2 秒輪詢一次最新狀態
  pollTimer = setInterval(() => {
    taskStore.fetchTasks();
  }, 2000);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});

const getStatusLabel = (status: string) => {
  switch (status) {
    case "pending":
      return "⏳ 待處理";
    case "downloading":
      return "🚀 下載中";
    case "completed":
      return "✅ 已完成";
    case "failed":
      return "❌ 失敗";
    default:
      return status;
  }
};
</script>

<template>
  <div class="view-container">
    <div class="header-row">
      <h2 class="title">📊 下載儀表板</h2>
      <div class="stats">
        <span>全部: {{ tasks.length }}</span> |
        <span class="text-success"
          >完成:
          {{ tasks.filter((t) => t.status === "completed").length }}</span
        >
        |
        <span class="text-error"
          >失敗: {{ tasks.filter((t) => t.status === "failed").length }}</span
        >
      </div>
    </div>

    <div v-if="tasks.length === 0" class="empty-state glass-card">
      <p>目前沒有下載中的任務。</p>
    </div>

    <div class="monitor-list scrollable">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="monitor-card glass-card"
        :class="task.status"
      >
        <div class="task-info">
          <div class="meta">
            <span class="anime">{{ task.anime_title }}</span>
            <span class="song" v-if="task.metadata"
              >{{ task.metadata.song_title }} - {{ task.metadata.artist }}</span
            >
          </div>
          <div class="status-badge" :class="task.status">
            {{ getStatusLabel(task.status) }}
          </div>
        </div>

        <div class="progress-section">
          <div class="progress-bar-container">
            <div
              class="progress-fill"
              :style="{ width: task.progress + '%' }"
            ></div>
          </div>
          <span class="percentage">{{ task.progress.toFixed(1) }}%</span>
        </div>

        <div v-if="task.error_message" class="error-msg">
          ⚠️ {{ task.error_message }}
        </div>

        <div class="footer">
          <span>來源: {{ task.source }}</span>
          <span>路徑: {{ task.target_dir }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-container {
  padding: 24px 40px;
  max-width: 1000px;
  margin: 0 auto;
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.stats {
  font-size: 14px;
  color: var(--text-muted);
}

.monitor-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 8px;
}

.monitor-card {
  padding: 16px 20px;
  border-left: 4px solid transparent;
}

.monitor-card.downloading {
  border-left-color: var(--primary);
}
.monitor-card.completed {
  border-left-color: #10b981;
}
.monitor-card.failed {
  border-left-color: #ef4444;
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.meta {
  display: flex;
  flex-direction: column;
}

.anime {
  font-weight: 700;
  font-size: 16px;
}

.song {
  font-size: 13px;
  color: var(--text-muted);
}

.status-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
}

.status-badge.downloading {
  color: var(--primary);
  background: rgba(99, 102, 241, 0.1);
}
.status-badge.completed {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}
.status-badge.failed {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.progress-bar-container {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), #8b5cf6);
  transition: width 0.3s ease;
}

.percentage {
  font-size: 12px;
  font-family: monospace;
  width: 45px;
  text-align: right;
}

.error-msg {
  font-size: 12px;
  color: #f87171;
  margin-top: 8px;
  padding: 8px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 4px;
}

.footer {
  margin-top: 12px;
  display: flex;
  gap: 20px;
  font-size: 11px;
  color: var(--text-muted);
}

.text-success {
  color: #10b981;
}
.text-error {
  color: #ef4444;
}

.empty-state {
  padding: 60px;
  text-align: center;
  color: var(--text-muted);
}
</style>
