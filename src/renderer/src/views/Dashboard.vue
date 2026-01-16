<script setup lang="ts">
import { useTaskStore } from "../store/useTaskStore";
const taskStore = useTaskStore();
</script>

<template>
  <div class="view-container">
    <div class="glass-card dashboard">
      <h2>📊 下載儀表板</h2>
      <p>檢視目前下載進度</p>
    </div>
  </div>
</template>

<style scoped>
.view-container {
  padding: 40px;
}
.dashboard {
  padding: 32px;
}
</style>
