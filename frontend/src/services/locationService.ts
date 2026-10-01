import api from './api';
import { LocationRecord, PaginatedResponse } from '../types';

export interface LocationProcessResult {
  location_id: number;
  device_id: number;
  events: Array<{
    geofence_id: number;
    geofence_name?: string;
    event_type: string;
    previous_state: string;
    current_state: string;
  }>;
}

export const locationService = {
  sendLocation: async (data: {
    device_id: number;
    latitude: number;
    longitude: number;
    accuracy_meters?: number;
    timestamp?: string;
  }): Promise<LocationProcessResult> => {
    const response = await api.post<LocationProcessResult>('/locations', data);
    return response.data;
  },

  getLocations: async (params?: {
    page?: number;
    page_size?: number;
    device_id?: number;
    user_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<LocationRecord>> => {
    const response = await api.get<PaginatedResponse<LocationRecord>>('/locations', { params });
    return response.data;
  },

  getDeviceLocations: async (
    deviceId: number,
    params?: { page?: number; page_size?: number; start_date?: string; end_date?: string }
  ): Promise<PaginatedResponse<LocationRecord>> => {
    const response = await api.get<PaginatedResponse<LocationRecord>>(`/locations/device/${deviceId}`, { params });
    return response.data;
  },
};
