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
  <div class="max-w-4xl">
    <h2
      class="text-3xl font-bold mb-8 bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent"
    >
      🎬 批次任務初始化
    </h2>

    <div class="glass-card p-8 space-y-6">
      <!-- 動畫清單 -->
      <div class="flex flex-col gap-2">
        <label class="text-sm font-semibold text-slate-400 ml-1"
          >動畫清單 (每行一個標題)</label
        >
        <textarea
          v-model="rawTitles"
          class="input-field scrollable min-h-[200px] resize-none"
          placeholder="例如：
葬送的芙莉蓮
我推的孩子"
        ></textarea>
      </div>

      <div class="grid grid-cols-2 gap-6">
        <!-- 下載路徑 -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-slate-400 ml-1"
            >下載路徑</label
          >
          <input
            v-model="targetDir"
            type="text"
            class="input-field"
            placeholder="/path/to/downloads"
          />
        </div>

        <!-- 下載來源 -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-slate-400 ml-1"
            >下載來源</label
          >
          <select v-model="source" class="input-field cursor-pointer">
            <option :value="Source.YOUTUBE">YouTube (最佳音質/畫質)</option>
            <option :value="Source.DMHY">動漫花園 (BT 資源)</option>
          </select>
        </div>

        <!-- DMHY 模式 -->
        <div v-if="source === Source.DMHY" class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-slate-400 ml-1"
            >DMHY 模式</label
          >
          <select v-model="dmhyMode" class="input-field cursor-pointer">
            <option :value="DownloadMode.VIDEO">自動下載影片 (建議)</option>
            <option :value="DownloadMode.TORRENT">僅存儲種子檔案</option>
          </select>
        </div>

        <!-- Bangumi Token -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-slate-400 ml-1"
            >Bangumi Token (選填)</label
          >
          <input
            v-model="bangumiToken"
            type="password"
            class="input-field"
            placeholder="提高 API 成功率"
          />
        </div>
      </div>

      <!-- 送出按鈕 -->
      <div class="flex justify-end pt-4">
        <button
          class="btn-primary min-w-[200px]"
          @click="handleNext"
          :disabled="isProcessing"
        >
          {{ isProcessing ? "🚀 搜尋中..." : "下一步：校對元數據 ➔" }}
        </button>
      </div>
    </div>
  </div>
</template>
