from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict


class PointSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    point_order: Optional[int] = None


class GeofenceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    type: str = Field(..., pattern="^(CIRCLE|POLYGON)$")
    center_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    center_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    radius_meters: Optional[float] = Field(None, gt=0.0)
    is_active: bool = True
    points: Optional[List[PointSchema]] = None

    @model_validator(mode="after")
    def validate_geofence_type_data(self):
        if self.type == "CIRCLE":
            if self.center_latitude is None or self.center_longitude is None:
                raise ValueError("center_latitude and center_longitude are required for CIRCLE geofence")
            if self.radius_meters is None or self.radius_meters <= 0:
                raise ValueError("radius_meters must be greater than 0 for CIRCLE geofence")
        elif self.type == "POLYGON":
            if not self.points or len(self.points) < 3:
                raise ValueError("POLYGON geofence must have at least 3 points")
        return self


class GeofenceCreate(GeofenceBase):
    pass


class GeofenceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(CIRCLE|POLYGON)$")
    center_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    center_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    radius_meters: Optional[float] = Field(None, gt=0.0)
    is_active: Optional[bool] = None
    points: Optional[List[PointSchema]] = None


class GeofenceStatusUpdate(BaseModel):
    is_active: bool


class GeofenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    type: str
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None
    radius_meters: Optional[float] = None
    is_active: bool
    created_by: Optional[int] = None
    creator_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    points: List[PointSchema] = []
