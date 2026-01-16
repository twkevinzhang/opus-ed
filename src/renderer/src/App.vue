<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskStore } from "./store/useTaskStore";

const taskStore = useTaskStore();

onMounted(() => {
  taskStore.fetchTasks();
});
</script>

<template>
  <div class="flex h-screen bg-[#0f172a]">
    <!-- Sidebar -->
    <aside class="w-64 glass-card m-4 mr-0 flex flex-col">
      <div class="p-8">
        <h1 class="text-3xl font-bold font-outfit tracking-tighter">
          Opus<span class="text-indigo-500">ED</span>
        </h1>
        <p
          class="text-xs text-slate-400 mt-1 font-medium uppercase tracking-widest"
        >
          AI AI OP/ED Getter
        </p>
      </div>

      <nav class="flex-1 px-4 space-y-2">
        <router-link to="/batch-input" class="nav-item group">
          <span class="text-lg group-hover:scale-110 transition-transform"
            >📥</span
          >
          批次初始化
        </router-link>
        <router-link to="/preview-edit" class="nav-item group">
          <span class="text-lg group-hover:scale-110 transition-transform"
            >🔍</span
          >
          預覽與編輯
        </router-link>
        <router-link to="/dashboard" class="nav-item group">
          <span class="text-lg group-hover:scale-110 transition-transform"
            >📊</span
          >
          下載儀表板
        </router-link>
      </nav>

      <div class="p-4 border-t border-white/5">
        <div
          class="p-4 glass-card bg-white/5 text-[10px] text-slate-500 uppercase tracking-tighter"
        >
          Sidecar:
          <span class="text-emerald-500 font-bold ml-1">Stateless</span>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col p-8 overflow-hidden">
      <router-view v-slot="{ Component }">
        <transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="transform translate-y-4 opacity-0"
          enter-to-class="transform translate-y-0 opacity-100"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="transform translate-y-0 opacity-100"
          leave-to-class="transform translate-y--4 opacity-0"
          mode="out-in"
        >
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
@reference "./index.css";

.nav-item {
  @apply flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 font-semibold transition-all duration-200 
         hover:bg-white/5 hover:text-white;
}

.router-link-active {
  @apply bg-indigo-500/10 text-white shadow-lg shadow-indigo-500/10 border border-indigo-500/20;
}
</style>
