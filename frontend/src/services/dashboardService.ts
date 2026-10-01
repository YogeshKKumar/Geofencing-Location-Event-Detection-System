import api from './api';
import { DashboardSummary, DeviceStatus, GeofenceStatus, GeofenceEvent } from '../types';

export const dashboardService = {
  getSummary: async (): Promise<DashboardSummary> => {
    const response = await api.get<DashboardSummary>('/dashboard/summary');
    return response.data;
  },

  getRecentEvents: async (limit: number = 10): Promise<GeofenceEvent[]> => {
    const response = await api.get<GeofenceEvent[]>('/dashboard/recent-events', { params: { limit } });
    return response.data;
  },

  getDeviceStatuses: async (): Promise<DeviceStatus[]> => {
    const response = await api.get<DeviceStatus[]>('/dashboard/device-status');
    return response.data;
  },

  getGeofenceStatuses: async (): Promise<GeofenceStatus[]> => {
    const response = await api.get<GeofenceStatus[]>('/dashboard/geofence-status');
    return response.data;
  },
};
