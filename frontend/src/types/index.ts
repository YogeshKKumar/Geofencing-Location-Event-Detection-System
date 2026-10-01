export type UserRole = 'ADMIN' | 'USER';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Device {
  id: number;
  device_identifier: string;
  name: string;
  user_id: number | null;
  user_name?: string | null;
  is_active: boolean;
  last_latitude: number | null;
  last_longitude: number | null;
  last_location_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Point {
  latitude: number;
  longitude: number;
  point_order?: number;
}

export type GeofenceType = 'CIRCLE' | 'POLYGON';

export interface Geofence {
  id: number;
  name: string;
  description?: string | null;
  type: GeofenceType;
  center_latitude?: number | null;
  center_longitude?: number | null;
  radius_meters?: number | null;
  is_active: boolean;
  created_by?: number | null;
  creator_name?: string | null;
  created_at: string;
  updated_at: string;
  points: Point[];
}

export interface LocationRecord {
  id: number;
  device_id: number;
  device_name?: string | null;
  user_id?: number | null;
  latitude: number;
  longitude: number;
  accuracy_meters: number;
  timestamp: string;
  created_at: string;
}

export type EventType = 'ENTER' | 'EXIT' | 'INSIDE' | 'OUTSIDE';
export type GeofenceState = 'INSIDE' | 'OUTSIDE' | 'UNKNOWN';

export interface GeofenceEvent {
  id: number;
  device_id: number;
  device_name?: string | null;
  user_id?: number | null;
  user_name?: string | null;
  geofence_id: number;
  geofence_name?: string | null;
  location_event_id?: number | null;
  event_type: EventType;
  previous_state: GeofenceState;
  current_state: GeofenceState;
  latitude: number;
  longitude: number;
  accuracy_meters: number;
  timestamp: string;
  created_at: string;
}

export interface DashboardSummary {
  total_users: number;
  total_devices: number;
  active_devices: number;
  active_geofences: number;
  events_today: number;
  enter_events: number;
  exit_events: number;
  devices_currently_inside: number;
  devices_currently_outside: number;
}

export interface DeviceStatus {
  device_id: number;
  device_name: string;
  device_identifier: string;
  is_active: boolean;
  last_latitude?: number | null;
  last_longitude?: number | null;
  last_location_at?: string | null;
  user_name?: string | null;
  current_state: string;
  inside_geofences: string[];
}

export interface GeofenceStatus {
  geofence_id: number;
  geofence_name: string;
  type: string;
  is_active: boolean;
  current_device_count: number;
  devices_inside: string[];
}

export interface AuditLog {
  id: number;
  user_id?: number | null;
  user_name?: string | null;
  action: string;
  entity_type: string;
  entity_id?: number | null;
  old_value?: any;
  new_value?: any;
  ip_address?: string | null;
  created_at: string;
}

export interface Pagination {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: Pagination;
}

export interface StandardResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}
