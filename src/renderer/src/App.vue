<script setup lang="ts">
// 範例：使用 TypeScript
const versions = { ...window.electron?.process.versions };
</script>

<template>
  <div class="container">
    <h1>OpusED TypeScript + DDD 初始化完成</h1>
    <div class="versions">
      <p>Electron v{{ versions.electron }}</p>
      <p>Node v{{ versions.node }}</p>
      <p>Vite v{{ versions.vite }}</p>
    </div>
    <div class="status-box">
      <p>MCP 遠端除錯埠 9222 已配置</p>
      <p>架構風格: DDD (domain, application, infrastructure)</p>
    </div>
  </div>
</template>

<style scoped>
.container {
  font-family: "Inter", system-ui, sans-serif;
  text-align: center;
  padding: 40px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  height: 100vh;
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
