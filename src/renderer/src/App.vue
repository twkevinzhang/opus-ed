<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskStore } from "./store/useTaskStore";

const taskStore = useTaskStore();

onMounted(() => {
  taskStore.fetchTasks();
});
</script>

<template>
  <div class="app-wrapper">
    <!-- 頂部裝飾列 -->
    <header class="top-nav glass-card">
      <div class="logo">Opus<span>ED</span></div>
      <nav class="nav-links">
        <router-link to="/batch-input" class="nav-item">批次初始化</router-link>
        <router-link to="/preview-edit" class="nav-item"
          >預覽與編輯</router-link
        >
        <router-link to="/dashboard" class="nav-item">儀表板</router-link>
      </nav>
    </header>

    <main class="content-area">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style>
.app-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.versions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin: 20px 0;
  font-family: monospace;
}
.status-box {
  background: #2d2d2d;
  border-left: 4px solid #646cff;
  padding: 15px;
  max-width: 500px;
  margin: 0 auto;
}
</style>
