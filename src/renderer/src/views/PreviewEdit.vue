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
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex justify-between items-center mb-8">
      <h2
        class="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent"
      >
        🔍 預覽與校對 ({{ tasks.length }})
      </h2>
      <button
        class="btn-primary"
        @click="handleStartAll"
        :disabled="tasks.length === 0"
      >
        🚀 啟動所有任務下載
      </button>
    </div>

    <!-- 空狀態 -->
    <div
      v-if="tasks.length === 0"
      class="flex-1 flex items-center justify-center"
    >
      <div class="glass-card p-12 text-center max-w-md">
        <p class="text-slate-400 text-lg">
          目前沒有待處理的任務，請先前往「批次初始化」頁面。
        </p>
      </div>
    </div>

    <!-- 任務清單 -->
    <div v-else class="flex-1 scrollable space-y-4">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="glass-card p-6 group transition-all duration-300 hover:translate-x-1"
      >
        <div class="flex justify-between items-start mb-4">
          <span
            class="text-xl font-bold text-indigo-400 flex items-center gap-2"
          >
            <span class="w-2 h-6 bg-indigo-500 rounded-full"></span>
            {{ task.anime_title }}
          </span>
          <button
            class="text-slate-500 hover:text-red-500 transition-colors p-1"
            @click="removeTask(task.id)"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <!-- 元數據輸入 -->
          <div v-if="task.metadata" class="grid grid-cols-6 gap-4">
            <div class="col-span-1 flex flex-col gap-1">
              <label
                class="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1"
                >類型</label
              >
              <input
                v-model="task.metadata.type"
                type="text"
                class="input-field !py-2 !px-3"
                placeholder="OP/ED"
              />
            </div>
            <div class="col-span-2 flex flex-col gap-1">
              <label
                class="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1"
                >歌曲名稱</label
              >
              <input
                v-model="task.metadata.song_title"
                type="text"
                class="input-field !py-2 !px-3"
                placeholder="標題"
              />
            </div>
            <div class="col-span-3 flex flex-col gap-1">
              <label
                class="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1"
                >演唱者</label
              >
              <input
                v-model="task.metadata.artist"
                type="text"
                class="input-field !py-2 !px-3"
                placeholder="歌手"
              />
            </div>
          </div>
          <div
            v-else
            class="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 text-amber-500 text-sm flex items-center gap-2"
          >
            <span>⚠️</span> 未獲取到自動元數據，請手動輸入關鍵字搜尋。
          </div>

          <!-- 自定義關鍵字 -->
          <div class="flex flex-col gap-1">
            <label
              class="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1"
              >自定義搜尋關鍵字 (覆蓋自動生成字串)</label
            >
            <input
              v-model="task.custom_keywords"
              type="text"
              class="input-field !py-2 !px-3 bg-indigo-500/5 focus:bg-indigo-500/10 placeholder:text-slate-600"
              placeholder="例如：動畫名 OP 無損"
            />
          </div>
        </div>

        <!-- 頁尾資訊 -->
        <div class="flex items-center gap-4 mt-6 pt-4 border-t border-white/5">
          <div class="flex items-center gap-2">
            <span
              class="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-tighter"
              :class="
                task.source === 'youtube'
                  ? 'bg-red-500 text-white'
                  : 'bg-emerald-500 text-white'
              "
            >
              {{ task.source }}
            </span>
            <span
              v-if="task.dmhy_mode"
              class="px-2 py-0.5 rounded bg-slate-700 text-white text-[10px] font-bold uppercase"
            >
              {{ task.dmhy_mode }}
            </span>
          </div>
          <span
            class="text-[11px] text-slate-500 flex items-center gap-1 font-medium"
          >
            <span class="opacity-50 text-base">📂</span> {{ task.target_dir }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
