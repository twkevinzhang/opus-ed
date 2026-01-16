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
  <div class="flex flex-col h-full overflow-hidden">
    <!-- 標題與統計 -->
    <div class="flex justify-between items-end mb-8">
      <div>
        <h2
          class="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent"
        >
          📊 下載儀表板
        </h2>
        <div
          class="flex gap-4 mt-2 text-xs font-bold uppercase tracking-widest text-slate-500"
        >
          <span>全部: {{ tasks.length }}</span>
          <span class="text-emerald-500"
            >完成:
            {{ tasks.filter((t) => t.status === "completed").length }}</span
          >
          <span class="text-red-500"
            >失敗: {{ tasks.filter((t) => t.status === "failed").length }}</span
          >
        </div>
      </div>
    </div>

    <!-- 空狀態 -->
    <div
      v-if="tasks.length === 0"
      class="flex-1 flex items-center justify-center"
    >
      <div class="glass-card p-12 text-center max-w-md">
        <p class="text-slate-400 text-lg">目前沒有下載中的任務。</p>
      </div>
    </div>

    <!-- 監控清單 -->
    <div v-else class="flex-1 scrollable space-y-3">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="glass-card p-5 border-l-4 transition-all duration-300"
        :class="{
          'border-indigo-500 bg-indigo-500/5': task.status === 'downloading',
          'border-emerald-500 bg-emerald-500/5': task.status === 'completed',
          'border-red-500 bg-red-500/5': task.status === 'failed',
          'border-slate-700': task.status === 'pending',
        }"
      >
        <div class="flex justify-between items-start mb-3">
          <div class="flex flex-col">
            <span class="font-bold text-slate-200">{{ task.anime_title }}</span>
            <span
              v-if="task.metadata"
              class="text-xs text-slate-500 font-medium"
            >
              {{ task.metadata.song_title }} - {{ task.metadata.artist }}
            </span>
          </div>
          <div
            class="text-[10px] font-black uppercase tracking-tighter px-2 py-1 rounded"
            :class="{
              'bg-indigo-500/20 text-indigo-400': task.status === 'downloading',
              'bg-emerald-500/20 text-emerald-400': task.status === 'completed',
              'bg-red-500/20 text-red-400': task.status === 'failed',
              'bg-slate-800 text-slate-500': task.status === 'pending',
            }"
          >
            {{ getStatusLabel(task.status) }}
          </div>
        </div>

        <!-- 進度條 -->
        <div class="flex items-center gap-4">
          <div class="flex-1 h-1.5 bg-slate-900 rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500 ease-out"
              :style="{ width: task.progress + '%' }"
            ></div>
          </div>
          <span
            class="text-[10px] font-mono font-bold text-slate-400 w-10 text-right"
          >
            {{ task.progress.toFixed(1) }}%
          </span>
        </div>

        <!-- 錯誤訊息 -->
        <div
          v-if="task.error_message"
          class="mt-3 p-2 bg-red-500/10 border border-red-500/20 rounded text-[10px] text-red-400 font-medium flex items-center gap-2"
        >
          <span>⚠️</span> {{ task.error_message }}
        </div>

        <!-- 頁尾 -->
        <div
          class="mt-3 pt-3 border-t border-white/5 flex gap-4 text-[10px] font-bold text-slate-600 uppercase tracking-widest"
        >
          <span class="flex items-center gap-1"
            ><span class="text-base leading-none">🌐</span>
            {{ task.source }}</span
          >
          <span class="flex items-center gap-1"
            ><span class="text-base leading-none">📂</span>
            {{ task.target_dir }}</span
          >
        </div>
      </div>
    </div>
  </div>
</template>
