from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.event_service import EventService
from app.schemas.event import GeofenceEventResponse
from app.schemas.common import PaginatedResponse, PaginationMetadata
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])


def _map_event_response(ev) -> GeofenceEventResponse:
    return GeofenceEventResponse(
        id=ev.id,
        device_id=ev.device_id,
        device_name=ev.device.name if ev.device else None,
        user_id=ev.user_id,
        user_name=ev.user.name if ev.user else None,
        geofence_id=ev.geofence_id,
        geofence_name=ev.geofence.name if ev.geofence else None,
        location_event_id=ev.location_event_id,
        event_type=ev.event_type,
        previous_state=ev.previous_state,
        current_state=ev.current_state,
        latitude=ev.latitude,
        longitude=ev.longitude,
        accuracy_meters=ev.accuracy_meters,
        timestamp=ev.timestamp,
        created_at=ev.created_at,
    )


@router.get("", response_model=PaginatedResponse[GeofenceEventResponse], summary="List geofence events with filters")
def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    device_id: Optional[int] = None,
    user_id: Optional[int] = None,
    geofence_id: Optional[int] = None,
    event_type: Optional[str] = Query(None, pattern="^(ENTER|EXIT|INSIDE|OUTSIDE)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = EventService(db)
    target_user_id = user_id
    if current_user.role != "ADMIN":
        target_user_id = current_user.id

    skip = (page - 1) * page_size
    events, total = service.list_events(
        skip=skip,
        limit=page_size,
        device_id=device_id,
        user_id=target_user_id,
        geofence_id=geofence_id,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[GeofenceEventResponse](
        success=True,
        data=[_map_event_response(e) for e in events],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{event_id}", response_model=GeofenceEventResponse, summary="Get event details by ID")
def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = EventService(db)
    ev = service.get_event_by_id(event_id)
    return _map_event_response(ev)


@router.get("/device/{device_id}", response_model=PaginatedResponse[GeofenceEventResponse], summary="List events for a specific device")
def get_device_events(
    device_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = EventService(db)
    skip = (page - 1) * page_size
    events, total = service.list_events(
        skip=skip,
        limit=page_size,
        device_id=device_id,
        event_type=event_type,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[GeofenceEventResponse](
        success=True,
        data=[_map_event_response(e) for e in events],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/geofence/{geofence_id}", response_model=PaginatedResponse[GeofenceEventResponse], summary="List events for a specific geofence")
def get_geofence_events(
    geofence_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = EventService(db)
    skip = (page - 1) * page_size
    events, total = service.list_events(
        skip=skip,
        limit=page_size,
        geofence_id=geofence_id,
        event_type=event_type,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[GeofenceEventResponse](
        success=True,
        data=[_map_event_response(e) for e in events],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )
