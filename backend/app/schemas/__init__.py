from app.schemas.common import StandardResponse, ErrorResponse, PaginationMetadata, PaginatedResponse
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.device import DeviceBase, DeviceCreate, DeviceUpdate, DeviceStatusUpdate, DeviceResponse
from app.schemas.geofence import PointSchema, GeofenceBase, GeofenceCreate, GeofenceUpdate, GeofenceStatusUpdate, GeofenceResponse
from app.schemas.location import LocationInput, LocationResponse, LocationEventTransition, LocationProcessResponse
from app.schemas.event import GeofenceEventResponse
from app.schemas.dashboard import DashboardSummary, DeviceStatusSummary, GeofenceStatusSummary
from app.schemas.audit_log import AuditLogResponse

__all__ = [
    "StandardResponse",
    "ErrorResponse",
    "PaginationMetadata",
    "PaginatedResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "DeviceBase",
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceStatusUpdate",
    "DeviceResponse",
    "PointSchema",
    "GeofenceBase",
    "GeofenceCreate",
    "GeofenceUpdate",
    "GeofenceStatusUpdate",
    "GeofenceResponse",
    "LocationInput",
    "LocationResponse",
    "LocationEventTransition",
    "LocationProcessResponse",
    "GeofenceEventResponse",
    "DashboardSummary",
    "DeviceStatusSummary",
    "GeofenceStatusSummary",
    "AuditLogResponse",
]
