import { api } from '../axiosClient';
import type { APIKey, APIKeyCreateResult } from "@/api/auth/types";

export const getApiKeys = async (): Promise<APIKey[]> => {
  const response = await api.get(`/api/apikeys/me`);
  return response.data;
};


export const getUserApiKeys = async (user_id: string): Promise<APIKey[]> => {
  const response = await api.get(`/api/apikeys/${user_id}`);
  return response.data;
};


export const deleteApiKey = async (keyId: string): Promise<void> => {
  const response = await api.delete(`/api/apikeys/${keyId}`);
  return response.data;
}

export const createApiKey = async (name: string): Promise<APIKeyCreateResult> => {
  const response = await api.post(`/api/apikeys`, { name });
  return response.data;
}