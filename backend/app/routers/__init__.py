from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.devices import router as devices_router
from app.routers.geofences import router as geofences_router
from app.routers.locations import router as locations_router
from app.routers.events import router as events_router
from app.routers.dashboard import router as dashboard_router
from app.routers.audit_logs import router as audit_logs_router

__all__ = [
    "auth_router",
    "users_router",
    "devices_router",
    "geofences_router",
    "locations_router",
    "events_router",
    "dashboard_router",
    "audit_logs_router",
]
