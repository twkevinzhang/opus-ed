<script setup lang="ts">
import { useTaskStore } from "../store/useTaskStore";
import { useRouter } from "vue-router";

const taskStore = useTaskStore();
const router = useRouter();

const handleStart = () => {
  // TODO: 串接下載 API
  router.push("/dashboard");
};
</script>

<template>
  <div class="view-container">
    <div class="glass-card preview-list">
      <h2>🔍 預覽與編輯</h2>
      <p>正在校對動畫資訊...</p>

      <div class="actions">
        <button class="btn-primary" @click="handleStart">確認並開始下載</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-container {
  padding: 40px;
}
.preview-list {
  padding: 32px;
}
</style>
