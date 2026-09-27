import { api } from "@/api/axiosClient";

export const loginApi = async (username: string, password: string) => {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  const response = await api.post(
    '/api/auth/login',
    formData,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    
  );
  return response.data;
};

export const loginMfaApi = async (mfaCode: string, mfaToken: string) => {
  const response = await api.post(
    '/api/auth/login/mfa',
    { mfa_code: mfaCode, mfa_token: mfaToken}
  );
  return response.data;
};

export const logoutApi = async () => {
  const response = await api.post('/api/auth/logout');
  return response;
};