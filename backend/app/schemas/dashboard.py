from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.event import GeofenceEventResponse


class DashboardSummary(BaseModel):
    total_users: int
    total_devices: int
    active_devices: int
    active_geofences: int
    events_today: int
    enter_events: int
    exit_events: int
    devices_currently_inside: int
    devices_currently_outside: int


class DeviceStatusSummary(BaseModel):
    device_id: int
    device_name: str
    device_identifier: str
    is_active: bool
    last_latitude: Optional[float] = None
    last_longitude: Optional[float] = None
    last_location_at: Optional[datetime] = None
    user_name: Optional[str] = None
    current_state: str  # "INSIDE", "OUTSIDE", or "UNKNOWN"
    inside_geofences: List[str] = []


class GeofenceStatusSummary(BaseModel):
    geofence_id: int
    geofence_name: str
    type: str
    is_active: bool
    current_device_count: int
    devices_inside: List[str] = []
