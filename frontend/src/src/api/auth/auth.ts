import { api } from "@/api/axiosClient";

export const loginApi = async (username: string, password: string, rememberMe: boolean) => {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);
  formData.append("remember_me", String(rememberMe));

  const response = await api.post(
    '/api/auth/login',
    formData,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    
  );
  return response.data;
};

export const loginMfaApi = async (mfaCode: string, mfaToken: string, rememberMe: boolean) => {
  const response = await api.post(
    '/api/auth/login/mfa',
    { mfa_code: mfaCode, mfa_token: mfaToken, remember_me: rememberMe }
  );
  return response.data;
};

export const logoutApi = async () => {
  const response = await api.post('/api/auth/logout');
  return response;
};

export const requestPasswordResetApi = async (email: string) => {
  const response = await api.post('/api/users/forgot_password', { email });
  return response.data;
};

export const changePasswordApi = async (token: string, plainPassword: string) => {
  const response = await api.patch(
    `/api/users/change_password/${encodeURIComponent(token)}`,
    { plain_password: plainPassword },
  );
  return response.data;
};

export const activateAccountApi = async (token: string) => {
  const response = await api.patch(
    `/api/users/activate/${encodeURIComponent(token)}`,
  );
  return response.data;
};