import { app } from "electron";
import path from "path";
import fs from "fs-extra";
import axios from "axios";
import { Task, TaskStatus } from "../../shared/models";

const SIDECAR_URL = "http://127.0.0.1:8000";

export class TaskRepository {
  private activeTasksPath: string;
  private historyPath: string;
  private tasksCache: Task[] = [];
  private saveTimer: NodeJS.Timeout | null = null;
  private readonly DEBOUNCE_MS = 2000;

  constructor() {
    const userDataPath = app.getPath("userData");
    const dataDir = path.join(userDataPath, "data");
    fs.ensureDirSync(dataDir);
    this.activeTasksPath = path.join(dataDir, "tasks.json");
    this.historyPath = path.join(dataDir, "history.json");

    if (!fs.existsSync(this.activeTasksPath)) {
      fs.writeJsonSync(this.activeTasksPath, []);
    }
    if (!fs.existsSync(this.historyPath)) {
      fs.writeJsonSync(this.historyPath, []);
    }

    this.loadFromDisk();
  }

  get activeTasksFilePath(): string {
    return this.activeTasksPath;
  }

  get historyFilePath(): string {
    return this.historyPath;
  }

  private loadFromDisk(): void {
    try {
      this.tasksCache = fs.readJsonSync(this.activeTasksPath);
    } catch (error) {
      console.error("Failed to load tasks from disk, resetting cache.", error);
      this.tasksCache = [];
    }
  }

  async getAllTasks(): Promise<Task[]> {
    // 從 Sidecar 獲取所有活躍任務的實時狀態
    try {
      const response = await axios.get(`${SIDECAR_URL}/tasks`);
      console.log("[TaskRepository] Sidecar /tasks response:", response.data);
      const sidecarTasks = response.data as Array<{
        task_id: string;
        anime_title: string;
        status: string;
        progress: number;
        error_message: string | null;
        source: string;
        target_dir: string;
        metadata: {
          anime_title: string;
          song_title: string;
          artist: string;
          type: string;
        } | null;
      }>;

      console.log("[TaskRepository] Local tasks cache:", this.tasksCache.map(t => ({ id: t.id, status: t.status })));

      // 將 Sidecar 的任務狀態合併到本地緩存
      for (const st of sidecarTasks) {
        const localTask = this.tasksCache.find((t) => t.id === st.task_id);
        console.log(`[TaskRepository] Matching task_id=${st.task_id}, found=${!!localTask}`);
        if (localTask) {
          // 更新本地任務的狀態
          localTask.status = st.status as TaskStatus;
          localTask.progress = st.progress;
          localTask.error_message = st.error_message ?? undefined;
          localTask.updated_at = new Date().toISOString();

          // 如果任務完成或失敗，保存到磁碟
          if (
            st.status === TaskStatus.COMPLETED ||
            st.status === TaskStatus.FAILED
          ) {
            await this.saveTask(localTask, true);
          }
        }
      }
    } catch (error) {
      // Sidecar 可能未啟動，忽略錯誤，返回本地緩存
      console.warn("Failed to fetch tasks from Sidecar:", error);
    }

    return this.tasksCache;
  }

  async getHistory(): Promise<Task[]> {
    return await fs.readJson(this.historyPath);
  }

  async getById(taskId: string): Promise<Task | undefined> {
    return this.tasksCache.find((t) => t.id === taskId);
  }

  async saveTask(task: Task, forcePersist = false): Promise<void> {
    const index = this.tasksCache.findIndex((t) => t.id === task.id);
    if (index !== -1) {
      this.tasksCache[index] = task;
    } else {
      this.tasksCache.push(task);
    }

    if (
      forcePersist ||
      task.status === TaskStatus.COMPLETED ||
      task.status === TaskStatus.FAILED
    ) {
      this.flush();
    } else {
      this.scheduleFlush();
    }
  }

  async saveBatchTasks(newTasks: Task[]): Promise<void> {
    this.tasksCache.push(...newTasks);
    this.flush();
  }

  async deleteTask(taskId: string): Promise<void> {
    this.tasksCache = this.tasksCache.filter((t) => t.id !== taskId);

    // 同時從 Sidecar 移除任務
    try {
      await axios.delete(`${SIDECAR_URL}/tasks/${taskId}`);
    } catch (error) {
      // 忽略錯誤，可能任務不存在於 Sidecar
    }

    this.flush();
  }

  async moveToHistory(task: Task): Promise<void> {
    this.tasksCache = this.tasksCache.filter((t) => t.id !== task.id);
    try {
      const history = await this.getHistory();
      history.push(task);
      await fs.writeJson(this.historyPath, history, { spaces: 2 });
    } catch (e) {
      console.error("Failed to write history:", e);
    }
    this.flush();
  }

  private scheduleFlush(): void {
    if (this.saveTimer) {
      clearTimeout(this.saveTimer);
    }
    this.saveTimer = setTimeout(() => {
      this.flush();
    }, this.DEBOUNCE_MS);
  }

  private flush(): void {
    if (this.saveTimer) {
      clearTimeout(this.saveTimer);
      this.saveTimer = null;
    }
    fs.writeJson(this.activeTasksPath, this.tasksCache, { spaces: 2 }).catch(
      (err) => console.error("Failed to flush tasks to disk:", err)
    );
  }
}
