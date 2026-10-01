from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.dashboard_service import DashboardService
from app.services.event_service import EventService
from app.schemas.dashboard import DashboardSummary, DeviceStatusSummary, GeofenceStatusSummary
from app.schemas.event import GeofenceEventResponse
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary, summary="Get high-level dashboard summary metrics")
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    return service.get_summary()


@router.get("/recent-events", response_model=List[GeofenceEventResponse], summary="Get recent geofence events")
def get_recent_events(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = EventService(db)
    events, _ = service.list_events(skip=0, limit=limit)
    from app.routers.events import _map_event_response
    return [_map_event_response(e) for e in events]


@router.get("/device-status", response_model=List[DeviceStatusSummary], summary="Get current status of all devices and active geofences")
def get_device_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    return service.get_device_statuses()


@router.get("/geofence-status", response_model=List[GeofenceStatusSummary], summary="Get occupancy status for all geofences")
def get_geofence_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    return service.get_geofence_statuses()
