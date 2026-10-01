import api from './api';
import { GeofenceEvent, PaginatedResponse } from '../types';

export const eventService = {
  getEvents: async (params?: {
    page?: number;
    page_size?: number;
    device_id?: number;
    user_id?: number;
    geofence_id?: number;
    event_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<GeofenceEvent>> => {
    const response = await api.get<PaginatedResponse<GeofenceEvent>>('/events', { params });
    return response.data;
  },

  getEventById: async (id: number): Promise<GeofenceEvent> => {
    const response = await api.get<GeofenceEvent>(`/events/${id}`);
    return response.data;
  },

  getDeviceEvents: async (
    deviceId: number,
    params?: { page?: number; page_size?: number; event_type?: string }
  ): Promise<PaginatedResponse<GeofenceEvent>> => {
    const response = await api.get<PaginatedResponse<GeofenceEvent>>(`/events/device/${deviceId}`, { params });
    return response.data;
  },

  getGeofenceEvents: async (
    geofenceId: number,
    params?: { page?: number; page_size?: number; event_type?: string }
  ): Promise<PaginatedResponse<GeofenceEvent>> => {
    const response = await api.get<PaginatedResponse<GeofenceEvent>>(`/events/geofence/${geofenceId}`, { params });
    return response.data;
  },
};
