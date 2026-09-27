// src/api/axiosClient.ts
import axios from 'axios';

export const api = axios.create({
  baseURL:'',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Zamiast window.location.href, wysyłamy sygnał do aplikacji
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
    return Promise.reject(error);
  }
);