import { api } from "@/api/axiosClient";

export type TaskContentType = "text" | "image" | "video";
export type TaskAnswerType = "text" | "single_choice" | "multiple_choice";

export type Task = {
  id: string;
  campaign_id: string;
  owner_id: string;
  reward: string;
  time_limit_minutes: number;
  required_assignments: number;
  task_content_type: TaskContentType;
  task_answer_type: TaskAnswerType;
  data_json: Record<string, unknown>;
};

export type TaskPage = {
  items: Task[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type TaskFilters = {
  page: number;
  page_size: number;
  reward_min?: string;
  reward_max?: string;
  time_limit_min?: string;
  time_limit_max?: string;
  reward_order?: "asc" | "desc";
  time_order?: "asc" | "desc";
  task_content_type?: TaskContentType;
  task_answer_type?: TaskAnswerType;
  owner_id?: string;
  campaign_id?: string;
};

export async function listTasks(filters: TaskFilters): Promise<TaskPage> {
  const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value !== "" && value !== undefined));
  const response = await api.get("/api/tasks", { params });
  return response.data;
}

export async function createTask(payload: Omit<Task, "id" | "owner_id">): Promise<Task> {
  const response = await api.post("/api/tasks", payload);
  return response.data;
}

export async function uploadTaskFiles(taskId: string, files: File[]) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const response = await api.post(`/api/tasks/${taskId}/files`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}
