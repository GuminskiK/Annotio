import { api } from "@/api/axiosClient";

export type Campaign = {
  id: string;
  title: string;
  description: string;
  total_budget: string;
  acceptance_strategy: "auto_48h" | "auditor_required";
  status: "draft" | "active" | "paused" | "finished";
};

export async function getMyCampaigns(): Promise<Campaign[]> {
  const response = await api.get("/api/campaigns/mine");
  return response.data;
}

export async function createCampaign(payload: Omit<Campaign, "id">): Promise<Campaign> {
  const response = await api.post("/api/campaigns", payload);
  return response.data;
}
