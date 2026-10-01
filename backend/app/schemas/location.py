from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class LocationInput(BaseModel):
    device_id: int
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180")
    accuracy_meters: float = Field(0.0, ge=0.0, description="GPS accuracy in meters (>= 0)")
    timestamp: Optional[datetime] = Field(None, description="ISO timestamp of location fix")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: Optional[datetime]) -> datetime:
        if v is None:
            return datetime.now(timezone.utc)

        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        if v > now + timedelta(days=1):
            raise ValueError("Timestamp cannot be more than 1 day in the future")
        if v < now - timedelta(days=365):
            raise ValueError("Timestamp is too old (older than 1 year)")
        return v


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    user_id: Optional[int] = None
    device_name: Optional[str] = None
    latitude: float
    longitude: float
    accuracy_meters: float
    timestamp: datetime
    created_at: datetime


class LocationEventTransition(BaseModel):
    geofence_id: int
    geofence_name: Optional[str] = None
    event_type: str  # ENTER, EXIT, INSIDE, OUTSIDE
    previous_state: str
    current_state: str


class LocationProcessResponse(BaseModel):
    location_id: int
    device_id: int
    events: List[LocationEventTransition]
