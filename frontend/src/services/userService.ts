import api from './api';
import { User, PaginatedResponse, Device } from '../types';

export const userService = {
  getUsers: async (params?: { page?: number; page_size?: number; search?: string; role?: string; is_active?: boolean }): Promise<PaginatedResponse<User>> => {
    const response = await api.get<PaginatedResponse<User>>('/users', { params });
    return response.data;
  },

  getUserById: async (id: number): Promise<User> => {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },

  createUser: async (data: { name: string; email: string; password: string; role: string; is_active?: boolean }): Promise<User> => {
    const response = await api.post<User>('/users', data);
    return response.data;
  },

  updateUser: async (id: number, data: { name?: string; email?: string; role?: string; is_active?: boolean; password?: string }): Promise<User> => {
    const response = await api.put<User>(`/users/${id}`, data);
    return response.data;
  },

  setUserStatus: async (id: number, is_active: boolean): Promise<User> => {
    const response = await api.patch<User>(`/users/${id}/status?is_active=${is_active}`);
    return response.data;
  },

  getUserDevices: async (id: number): Promise<PaginatedResponse<Device>> => {
    const response = await api.get<PaginatedResponse<Device>>(`/users/${id}/devices`);
    return response.data;
  },
};
