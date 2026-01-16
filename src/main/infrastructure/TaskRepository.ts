import { app } from "electron";
import fs from "fs-extra";
import path from "path";
import { Task } from "../../shared/models";

export class TaskRepository {
  private activeTasksPath: string;
  private historyPath: string;

  constructor() {
    const userDataPath = app.getPath("userData");
    const dataDir = path.join(userDataPath, "data");
    fs.ensureDirSync(dataDir);

    this.activeTasksPath = path.join(dataDir, "tasks.json");
    this.historyPath = path.join(dataDir, "history.json");

    // 初始化檔案
    if (!fs.existsSync(this._activeTasksPath))
      fs.writeJsonSync(this._activeTasksPath, []);
    if (!fs.existsSync(this._historyPath))
      fs.writeJsonSync(this._historyPath, []);
  }

  // 為了測試或備份方便，暴露路徑
  private get _activeTasksPath(): string {
    return this.activeTasksPath;
  }
  private get _historyPath(): string {
    return this.historyPath;
  }

  async getAllTasks(): Promise<Task[]> {
    return await fs.readJson(this._activeTasksPath);
  }

  async getHistory(): Promise<Task[]> {
    return await fs.readJson(this._historyPath);
  }

  async getById(taskId: string): Promise<Task | undefined> {
    const tasks = await this.getAllTasks();
    return tasks.find((t) => t.id === taskId);
  }

  async saveTask(task: Task): Promise<void> {
    const tasks = await this.getAllTasks();
    const index = tasks.findIndex((t) => t.id === task.id);
    if (index !== -1) {
      tasks[index] = task;
    } else {
      tasks.push(task);
    }
    await fs.writeJson(this._activeTasksPath, tasks, { spaces: 2 });
  }

  async saveBatchTasks(newTasks: Task[]): Promise<void> {
    const tasks = await this.getAllTasks();
    tasks.push(...newTasks);
    await fs.writeJson(this._activeTasksPath, tasks, { spaces: 2 });
  }

  async deleteTask(taskId: string): Promise<void> {
    const tasks = await this.getAllTasks();
    const filtered = tasks.filter((t) => t.id !== taskId);
    await fs.writeJson(this._activeTasksPath, filtered, { spaces: 2 });
  }

  async moveToHistory(task: Task): Promise<void> {
    // 1. 從活躍任務移除
    await this.deleteTask(task.id);

    // 2. 加入歷史紀錄
    const history = await this.getHistory();
    history.push(task);
    await fs.writeJson(this._historyPath, history, { spaces: 2 });
  }
}
