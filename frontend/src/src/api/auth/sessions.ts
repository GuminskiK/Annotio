import { api } from '../axiosClient';
import type { Session } from './types';

export const getSessions = async (): Promise<Session[]> => {

    const response = await api.get(`/api/sessions/me`);
    return response.data;

}

export const getUserSessions = async (userId: string): Promise<Session[]> => {

    const response = await api.get(`/api/sessions/${userId}`);
    return response.data;

}

export const deleteSession = async (sessionId: string): Promise<void> => {

    const response = await api.delete(`/api/sessions/${sessionId}`);
    return response.data;
}