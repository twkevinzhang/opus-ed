export enum Source {
  YOUTUBE = "youtube",
  DMHY = "dmhy",
}

export enum DownloadMode {
  VIDEO = "video",
  TORRENT = "torrent",
}

export enum TaskStatus {
  PENDING = "pending",
  DOWNLOADING = "downloading",
  COMPLETED = "completed",
  FAILED = "failed",
}

export interface Metadata {
  anime_title: string;
  song_title: string;
  artist: string;
  type: string; // e.g., "OP", "ED"
  bangumi_id?: string;
}

export interface Task {
  id: string;
  anime_title: string;
  target_dir: string;
  source: Source;
  dmhy_mode: DownloadMode;
  metadata?: Metadata;
  custom_keywords?: string;
  status: TaskStatus;
  progress: number;
  error_message?: string;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}
