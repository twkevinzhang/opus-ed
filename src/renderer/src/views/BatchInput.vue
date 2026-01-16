<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useTaskStore } from "../store/useTaskStore";
import { Source, DownloadMode } from "../../../shared/models";

const router = useRouter();
const taskStore = useTaskStore();

const rawTitles = ref("");
const targetDir = ref("");
const source = ref<Source>(Source.YOUTUBE);
const dmhyMode = ref<DownloadMode>(DownloadMode.VIDEO);
const bangumiToken = ref("");

const isProcessing = ref(false);

const handleNext = async () => {
  if (!rawTitles.value || !targetDir.value) {
    alert("請輸入動畫清單與下載路徑");
    return;
  }

  isProcessing.value = true;
  const titles = rawTitles.value
    .split("\n")
    .map((t) => t.trim())
    .filter((t) => t);

  try {
    await taskStore.createBatch({
      titles,
      targetDir: targetDir.value,
      source: source.value,
      dmhyMode: dmhyMode.value,
      token: bangumiToken.value,
    });
    router.push("/preview-edit");
  } catch (err) {
    console.error(err);
  } finally {
    isProcessing.value = false;
  }
};
</script>

<template>
  <div class="view-container">
    <div class="glass-card main-form">
      <h2 class="title">🎬 批次任務初始化</h2>

      <div class="input-group">
        <label>動畫清單 (每行一個標題)</label>
        <textarea
          v-model="rawTitles"
          class="input-field scrollable"
          placeholder="例如：
葬送的芙莉蓮
我推的孩子"
          rows="8"
        ></textarea>
      </div>

      <div class="grid-form">
        <div class="input-group">
          <label>下載路徑</label>
          <input
            v-model="targetDir"
            type="text"
            class="input-field"
            placeholder="/path/to/downloads"
          />
        </div>

        <div class="input-group">
          <label>下載來源</label>
          <select v-model="source" class="input-field">
            <option :value="Source.YOUTUBE">YouTube (最佳音質/畫質)</option>
            <option :value="Source.DMHY">動漫花園 (BT 資源)</option>
          </select>
        </div>

        <div v-if="source === Source.DMHY" class="input-group">
          <label>DMHY 模式</label>
          <select v-model="dmhyMode" class="input-field">
            <option :value="DownloadMode.VIDEO">自動下載影片 (建議)</option>
            <option :value="DownloadMode.TORRENT">僅存儲種子檔案</option>
          </select>
        </div>

        <div class="input-group">
          <label>Bangumi Token (選填)</label>
          <input
            v-model="bangumiToken"
            type="password"
            class="input-field"
            placeholder="提高 Bangumi API 取得率"
          />
        </div>
      </div>

      <div class="actions">
        <button
          class="btn-primary"
          @click="handleNext"
          :disabled="isProcessing"
        >
          {{ isProcessing ? "搜尋中..." : "下一步：校對元數據 ➔" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 40px;
}

.main-form {
  width: 100%;
  max-width: 800px;
  padding: 32px;
}

.title {
  margin-top: 0;
  margin-bottom: 24px;
  background: linear-gradient(135deg, white, var(--text-muted));
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.input-group label {
  font-size: 14px;
  color: var(--text-muted);
  font-weight: 600;
}

.grid-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

textarea {
  resize: vertical;
}
</style>
