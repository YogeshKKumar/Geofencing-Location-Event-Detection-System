from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class GeofenceEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    device_name: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    geofence_id: int
    geofence_name: Optional[str] = None
    location_event_id: Optional[int] = None
    event_type: str  # ENTER, EXIT, INSIDE, OUTSIDE
    previous_state: str  # INSIDE, OUTSIDE, UNKNOWN
    current_state: str   # INSIDE, OUTSIDE, UNKNOWN
    latitude: float
    longitude: float
    accuracy_meters: float
    timestamp: datetime
    created_at: datetime
