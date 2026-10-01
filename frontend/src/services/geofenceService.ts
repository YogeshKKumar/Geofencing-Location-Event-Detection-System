import api from './api';
import { Geofence, PaginatedResponse, StandardResponse, Point } from '../types';

export const geofenceService = {
  getGeofences: async (params?: { page?: number; page_size?: number; search?: string; type?: string; is_active?: boolean }): Promise<PaginatedResponse<Geofence>> => {
    const response = await api.get<PaginatedResponse<Geofence>>('/geofences', { params });
    return response.data;
  },

  getGeofenceById: async (id: number): Promise<Geofence> => {
    const response = await api.get<Geofence>(`/geofences/${id}`);
    return response.data;
  },

  createGeofence: async (data: {
    name: string;
    description?: string;
    type: 'CIRCLE' | 'POLYGON';
    center_latitude?: number | null;
    center_longitude?: number | null;
    radius_meters?: number | null;
    is_active?: boolean;
    points?: Point[];
  }): Promise<Geofence> => {
    const response = await api.post<Geofence>('/geofences', data);
    return response.data;
  },

  updateGeofence: async (id: number, data: {
    name?: string;
    description?: string;
    type?: 'CIRCLE' | 'POLYGON';
    center_latitude?: number | null;
    center_longitude?: number | null;
    radius_meters?: number | null;
    is_active?: boolean;
    points?: Point[];
  }): Promise<Geofence> => {
    const response = await api.put<Geofence>(`/geofences/${id}`, data);
    return response.data;
  },

  setGeofenceStatus: async (id: number, is_active: boolean): Promise<Geofence> => {
    const response = await api.patch<Geofence>(`/geofences/${id}/status`, { is_active });
    return response.data;
  },

  deleteGeofence: async (id: number): Promise<StandardResponse> => {
    const response = await api.delete<StandardResponse>(`/geofences/${id}`);
    return response.data;
  },
};
