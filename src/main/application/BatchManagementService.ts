import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import {
  Task,
  TaskStatus,
  Metadata,
  Source,
  DownloadMode,
} from "../../shared/models";
import { TaskRepository } from "../infrastructure/TaskRepository";

const SIDECAR_URL = "http://127.0.0.1:8000";

export class BatchManagementService {
  constructor(private taskRepo: TaskRepository) {}

  async createBatchTasks(
    titles: string[],
    targetDir: string,
    source: string,
    dmhyMode: string,
    bangumiToken?: string
  ): Promise<Task[]> {
    const newTasks: Task[] = [];

    for (const title of titles) {
      try {
        const response = await axios.get(`${SIDECAR_URL}/metadata/search`, {
          params: { title, token: bangumiToken },
        });
        const metas = response.data as Metadata[];

        if (!metas || metas.length === 0) {
          newTasks.push(this.createNewTask(title, targetDir, source, dmhyMode));
        } else {
          for (const meta of metas) {
            newTasks.push(
              this.createNewTask(
                meta.anime_title,
                targetDir,
                source,
                dmhyMode,
                meta
              )
            );
          }
        }
      } catch (error) {
        console.error(`搜尋動畫 "${title}" 失敗:`, error);
        newTasks.push(this.createNewTask(title, targetDir, source, dmhyMode));
      }
    }

    await this.taskRepo.saveBatchTasks(newTasks);
    return newTasks;
  }

  private createNewTask(
    animeTitle: string,
    targetDir: string,
    source: string,
    dmhyMode: string,
    metadata?: Metadata
  ): Task {
    const now = new Date().toISOString();
    return {
      id: uuidv4(),
      anime_title: animeTitle,
      target_dir: targetDir,
      source: source as Source,
      dmhy_mode: dmhyMode as DownloadMode,
      metadata,
      status: TaskStatus.PENDING,
      progress: 0,
      created_at: now,
      updated_at: now,
    };
  }

  async startDownload(taskId: string): Promise<void> {
    const task = await this.taskRepo.getById(taskId);
    if (!task) {
      console.error(`[BatchManagementService] Task ${taskId} not found`);
      return;
    }

    try {
      // 更新本地狀態為下載中
      task.status = TaskStatus.DOWNLOADING;
      task.progress = 0;
      task.updated_at = new Date().toISOString();
      await this.taskRepo.saveTask(task);

      // 調用 Sidecar 啟動下載（異步，立即返回）
      const response = await axios.post(`${SIDECAR_URL}/download`, {
        task_id: task.id, // 傳入本地 task ID，確保兩端一致
        anime_title: task.anime_title,
        target_dir: task.target_dir,
        source: task.source,
        dmhy_mode: task.dmhy_mode,
        metadata: task.metadata,
        custom_keywords: task.custom_keywords,
      });

      // 注意：進度更新通過 TaskRepository.getAllTasks() 輪詢 Sidecar 獲取
    } catch (error) {
      console.error("下載請求失敗:", error);
      task.status = TaskStatus.FAILED;
      task.error_message = `無法啟動下載: ${error}`;
      task.updated_at = new Date().toISOString();
      await this.taskRepo.saveTask(task);
    }
  }
}
