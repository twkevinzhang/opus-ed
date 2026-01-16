<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useTaskStore } from "../store/useTaskStore";

const taskStore = useTaskStore();
const router = useRouter();

const tasks = computed(() => taskStore.tasks);

const handleStartAll = async () => {
  const pendingTasks = tasks.value.filter((t) => t.status === "pending");
  for (const task of pendingTasks) {
    taskStore.startDownload(task.id);
  }
  router.push("/dashboard");
};

const removeTask = (id: string) => {
  taskStore.removeTask(id);
};
</script>

<template>
  <div class="view-container">
    <div class="header-row">
      <h2 class="title">🔍 預覽與校對 ({{ tasks.length }})</h2>
      <div class="global-actions">
        <button
          class="btn-primary"
          @click="handleStartAll"
          :disabled="tasks.length === 0"
        >
          🚀 啟動所有任務下載
        </button>
      </div>
    </div>

    <div v-if="tasks.length === 0" class="empty-state glass-card">
      <p>目前沒有待處理的任務，請先前往「批次初始化」頁面。</p>
    </div>

    <div class="task-list scrollable">
      <div v-for="task in tasks" :key="task.id" class="task-card glass-card">
        <div class="card-header">
          <span class="anime-title">{{ task.anime_title }}</span>
          <button
            class="btn-icon delete"
            @click="removeTask(task.id)"
            title="刪除任務"
          >
            ✕
          </button>
        </div>

        <div class="card-body">
          <div v-if="task.metadata" class="meta-inputs">
            <div class="input-block">
              <label>歌曲類型</label>
              <input
                v-model="task.metadata.type"
                type="text"
                class="input-field minimal"
                placeholder="OP/ED"
              />
            </div>
            <div class="input-block">
              <label>歌曲名稱</label>
              <input
                v-model="task.metadata.song_title"
                type="text"
                class="input-field minimal"
                placeholder="標題"
              />
            </div>
            <div class="input-block">
              <label>演唱者</label>
              <input
                v-model="task.metadata.artist"
                type="text"
                class="input-field minimal"
                placeholder="歌手"
              />
            </div>
          </div>
          <div v-else class="no-meta-warning">
            ⚠️ 未獲取到自動元數據，請手動輸入或在下方使用關鍵字搜尋。
          </div>

          <div class="keywords-block">
            <label>自定義搜尋關鍵字 (選填, 將覆蓋自動生成之字串)</label>
            <input
              v-model="task.custom_keywords"
              type="text"
              class="input-field minimal"
              placeholder="例如：動畫名 OP"
            />
          </div>
        </div>

        <div class="card-footer">
          <span class="source-badge" :class="task.source">{{
            task.source.toUpperCase()
          }}</span>
          <span v-if="task.dmhy_mode" class="mode-badge">{{
            task.dmhy_mode
          }}</span>
          <span class="path-text">📂 {{ task.target_dir }}</span>
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

.title {
  margin: 0;
  font-size: 28px;
  background: linear-gradient(135deg, white, var(--text-muted));
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.task-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 8px;
}

.task-card {
  padding: 20px;
  transition: transform 0.2s;
}

.task-card:hover {
  transform: translateX(4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.anime-title {
  font-family: "Outfit", sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}

.meta-inputs {
  display: grid;
  grid-template-columns: 80px 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.input-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input-block label,
.keywords-block label {
  font-size: 12px;
  color: var(--text-muted);
}

.input-field.minimal {
  padding: 8px 10px;
  background: rgba(0, 0, 0, 0.2);
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  font-size: 12px;
  color: var(--text-muted);
}

.source-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 800;
  font-size: 10px;
}

.source-badge.youtube {
  background: #ef4444;
  color: white;
}
.source-badge.dmhy {
  background: #10b981;
  color: white;
}

.mode-badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.btn-icon.delete {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 18px;
  opacity: 0.6;
}

.btn-icon.delete:hover {
  opacity: 1;
}

.empty-state {
  padding: 60px;
  text-align: center;
  color: var(--text-muted);
}
</style>
