import api from './api';
import { AuditLog, PaginatedResponse } from '../types';

export const auditService = {
  getLogs: async (params?: {
    page?: number;
    page_size?: number;
    action?: string;
    entity_type?: string;
    user_id?: number;
  }): Promise<PaginatedResponse<AuditLog>> => {
    const response = await api.get<PaginatedResponse<AuditLog>>('/audit-logs', { params });
    return response.data;
  },
};
