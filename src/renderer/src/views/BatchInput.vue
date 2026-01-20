<script setup lang="ts">
import { ref, onMounted } from "vue";
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

onMounted(async () => {
  const defaultPath = await window.api.getDownloadPath();
  if (defaultPath) {
    targetDir.value = defaultPath;
  }
});

const handleSelectDirectory = async () => {
  const path = await window.api.selectDirectory();
  if (path) {
    targetDir.value = path;
  }
};

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
          class="input-field scrollable min-h-[200px]"
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
          <div class="flex gap-2">
            <input
              v-model="targetDir"
              type="text"
              class="input-field flex-1"
              placeholder="/path/to/downloads"
            />
            <button
              type="button"
              @click="handleSelectDirectory"
              class="px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 rounded-lg transition-colors border border-slate-600/50 hover:border-slate-500"
              title="選擇資料夾"
            >
              📁
            </button>
          </div>
        </div>

        <!-- 下載來源 -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-slate-400 ml-1"
            >下載來源</label
          >
          <div
            class="flex p-1 bg-slate-800/50 rounded-xl border border-white/5 gap-1"
          >
            <button
              type="button"
              @click="source = Source.YOUTUBE"
              :class="[
                'flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200',
                source === Source.YOUTUBE
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-300 hover:bg-white/5 border border-transparent',
              ]"
            >
              YouTube
            </button>
            <button
              type="button"
              @click="source = Source.DMHY"
              :class="[
                'flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200',
                source === Source.DMHY
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-300 hover:bg-white/5 border border-transparent',
              ]"
            >
              動漫花園
            </button>
          </div>
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

        <!-- DMHY 模式 -->
        <div v-if="source === Source.DMHY" class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-slate-400 ml-1"
            >DMHY 模式</label
          >
          <div
            class="flex p-1 bg-slate-800/50 rounded-xl border border-white/5 gap-1"
          >
            <button
              type="button"
              @click="dmhyMode = DownloadMode.VIDEO"
              :class="[
                'flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200',
                dmhyMode === DownloadMode.VIDEO
                  ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  : 'text-slate-400 hover:text-slate-300 hover:bg-white/5 border border-transparent',
              ]"
            >
              自動下載影片
            </button>
            <button
              type="button"
              @click="dmhyMode = DownloadMode.TORRENT"
              :class="[
                'flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200',
                dmhyMode === DownloadMode.TORRENT
                  ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  : 'text-slate-400 hover:text-slate-300 hover:bg-white/5 border border-transparent',
              ]"
            >
              僅存儲種子
            </button>
          </div>
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
<style scoped>
.input-field::placeholder {
  color: color-mix(in srgb, var(--color-slate-500), transparent);
  opacity: 0.6;
}
</style>
