from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DeviceBase(BaseModel):
    device_identifier: str = Field(..., min_length=3, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)
    user_id: Optional[int] = None
    is_active: bool = True


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    user_id: Optional[int] = None
    is_active: Optional[bool] = None


class DeviceStatusUpdate(BaseModel):
    is_active: bool


class DeviceResponse(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_latitude: Optional[float] = None
    last_longitude: Optional[float] = None
    last_location_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user_name: Optional[str] = None
