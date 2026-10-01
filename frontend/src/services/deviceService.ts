import api from './api';
import { Device, PaginatedResponse, StandardResponse } from '../types';

export const deviceService = {
  getDevices: async (params?: { page?: number; page_size?: number; user_id?: number; is_active?: boolean; search?: string }): Promise<PaginatedResponse<Device>> => {
    const response = await api.get<PaginatedResponse<Device>>('/devices', { params });
    return response.data;
  },

  getDeviceById: async (id: number): Promise<Device> => {
    const response = await api.get<Device>(`/devices/${id}`);
    return response.data;
  },

  createDevice: async (data: { device_identifier: string; name: string; user_id?: number | null; is_active?: boolean }): Promise<Device> => {
    const response = await api.post<Device>('/devices', data);
    return response.data;
  },

  updateDevice: async (id: number, data: { name?: string; user_id?: number | null; is_active?: boolean }): Promise<Device> => {
    const response = await api.put<Device>(`/devices/${id}`, data);
    return response.data;
  },

  setDeviceStatus: async (id: number, is_active: boolean): Promise<Device> => {
    const response = await api.patch<Device>(`/devices/${id}/status`, { is_active });
    return response.data;
  },

  deleteDevice: async (id: number): Promise<StandardResponse> => {
    const response = await api.delete<StandardResponse>(`/devices/${id}`);
    return response.data;
  },
};
