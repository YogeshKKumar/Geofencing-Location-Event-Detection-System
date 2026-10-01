from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.location_service import LocationService
from app.schemas.location import LocationInput, LocationProcessResponse, LocationResponse
from app.schemas.common import PaginatedResponse, PaginationMetadata
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/locations", tags=["Locations"])


def _map_location_response(loc) -> LocationResponse:
    return LocationResponse(
        id=loc.id,
        device_id=loc.device_id,
        user_id=loc.user_id,
        device_name=loc.device.name if loc.device else None,
        latitude=loc.latitude,
        longitude=loc.longitude,
        accuracy_meters=loc.accuracy_meters,
        timestamp=loc.timestamp,
        created_at=loc.created_at,
    )


@router.post("", response_model=LocationProcessResponse, status_code=status.HTTP_200_OK, summary="Ingest GPS location and trigger geofence event detection")
def send_location(
    loc_in: LocationInput,
    request: Request,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    ip_addr = request.client.host if request.client else None
    service = LocationService(db)
    return service.process_location(
        location_in=loc_in,
        idempotency_key=idempotency_key,
        ip_address=ip_addr,
    )


@router.get("", response_model=PaginatedResponse[LocationResponse], summary="Get location history")
def list_locations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    device_id: Optional[int] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LocationService(db)
    target_user_id = user_id
    if current_user.role != "ADMIN":
        target_user_id = current_user.id

    skip = (page - 1) * page_size
    locations, total = service.list_locations(
        skip=skip,
        limit=page_size,
        device_id=device_id,
        user_id=target_user_id,
        start_date=start_date,
        end_date=end_date,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[LocationResponse](
        success=True,
        data=[_map_location_response(l) for l in locations],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/device/{device_id}", response_model=PaginatedResponse[LocationResponse], summary="Get location history for a specific device")
def get_device_locations(
    device_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LocationService(db)
    skip = (page - 1) * page_size
    locations, total = service.list_locations(
        skip=skip,
        limit=page_size,
        device_id=device_id,
        start_date=start_date,
        end_date=end_date,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[LocationResponse](
        success=True,
        data=[_map_location_response(l) for l in locations],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )
