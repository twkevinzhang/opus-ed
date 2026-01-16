import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import {
  Task,
  TaskStatus,
  Source,
  DownloadMode,
  Metadata,
} from "../../shared/models";
import { TaskRepository } from "../infrastructure/TaskRepository";

export class BatchManagementService {
  private sidecarUrl = "http://127.0.0.1:8000";

  constructor(private taskRepo: TaskRepository) {}

  async createBatchTasks(
    titles: string[],
    targetDir: string,
    source: Source,
    dmhyMode: DownloadMode,
    bangumiToken?: string
  ): Promise<Task[]> {
    const newTasks: Task[] = [];

    for (const title of titles) {
      try {
        // 向 Sidecar 請求元數據搜尋
        const response = await axios.get(`${this.sidecarUrl}/metadata/search`, {
          params: { title, token: bangumiToken },
        });

        const metas: Metadata[] = response.data;

        if (!metas || metas.length === 0) {
          // 沒找到元數據時，建立一個待編輯任務
          newTasks.push(
            this._createNewTask(title, targetDir, source, dmhyMode)
          );
        } else {
          for (const meta of metas) {
            newTasks.push(
              this._createNewTask(
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
        // 發生錯誤時仍建立基礎任務供手動輸入
        newTasks.push(this._createNewTask(title, targetDir, source, dmhyMode));
      }
    }

    await this.taskRepo.saveBatchTasks(newTasks);
    return newTasks;
  }

  private _createNewTask(
    animeTitle: string,
    targetDir: string,
    source: Source,
    dmhyMode: DownloadMode,
    metadata?: Metadata
  ): Task {
    const now = new Date().toISOString();
    return {
      id: uuidv4(),
      anime_title: animeTitle,
      target_dir: targetDir,
      source: source,
      dmhy_mode: dmhyMode,
      metadata: metadata,
      status: TaskStatus.PENDING,
      progress: 0,
      created_at: now,
      updated_at: now,
    };
  }

  async startDownload(taskId: string): Promise<void> {
    const task = await this.taskRepo.getById(taskId); // 注意：TaskRepository 需要增加這個方法
    if (!task) return;

    try {
      // 呼叫 Sidecar 下載
      const response = await axios.post(`${this.sidecarUrl}/download`, {
        anime_title: task.anime_title,
        target_dir: task.target_dir,
        source: task.source,
        dmhy_mode: task.dmhy_mode,
        metadata: task.metadata,
        custom_keywords: task.custom_keywords,
      });

      // 更新本地狀態
      const result = response.data;
      task.status = result.status;
      task.progress = result.progress;
      task.error_message = result.error_message;
      task.updated_at = new Date().toISOString();

      await this.taskRepo.saveTask(task);

      if (task.status === TaskStatus.COMPLETED) {
        await this.taskRepo.moveToHistory(task);
      }
    } catch (error) {
      task.status = TaskStatus.FAILED;
      task.error_message = `無法啟動下載: ${error}`;
      await this.taskRepo.saveTask(task);
    }
  }
}
