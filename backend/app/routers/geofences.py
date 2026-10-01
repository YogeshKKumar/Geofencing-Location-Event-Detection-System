from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.geofence_service import GeofenceService
from app.schemas.geofence import GeofenceCreate, GeofenceUpdate, GeofenceStatusUpdate, GeofenceResponse, PointSchema
from app.schemas.common import PaginatedResponse, PaginationMetadata, StandardResponse
from app.routers.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/geofences", tags=["Geofences"])


def _map_geofence_response(g) -> GeofenceResponse:
    pts = [
        PointSchema(latitude=p.latitude, longitude=p.longitude, point_order=p.point_order)
        for p in sorted(g.points, key=lambda x: x.point_order)
    ]
    return GeofenceResponse(
        id=g.id,
        name=g.name,
        description=g.description,
        type=g.type,
        center_latitude=g.center_latitude,
        center_longitude=g.center_longitude,
        radius_meters=g.radius_meters,
        is_active=g.is_active,
        created_by=g.created_by,
        creator_name=g.creator.name if g.creator else None,
        created_at=g.created_at,
        updated_at=g.updated_at,
        points=pts,
    )


@router.post("", response_model=GeofenceResponse, status_code=status.HTTP_201_CREATED, summary="Create a new geofence (Admin only)")
def create_geofence(
    geo_in: GeofenceCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = GeofenceService(db)
    created = service.create_geofence(geo_in, user_id=current_admin.id)
    return _map_geofence_response(created)


@router.get("", response_model=PaginatedResponse[GeofenceResponse], summary="List geofences")
def list_geofences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    type: Optional[str] = Query(None, alias="type"),
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = GeofenceService(db)
    skip = (page - 1) * page_size
    geofences, total = service.list_geofences(
        skip=skip, limit=page_size, search=search, geo_type=type, is_active=is_active
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[GeofenceResponse](
        success=True,
        data=[_map_geofence_response(g) for g in geofences],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{geofence_id}", response_model=GeofenceResponse, summary="Get geofence by ID")
def get_geofence(
    geofence_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = GeofenceService(db)
    geo = service.get_geofence_by_id(geofence_id)
    return _map_geofence_response(geo)


@router.put("/{geofence_id}", response_model=GeofenceResponse, summary="Update geofence (Admin only)")
def update_geofence(
    geofence_id: int,
    geo_in: GeofenceUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = GeofenceService(db)
    updated = service.update_geofence(geofence_id, geo_in, user_id=current_admin.id)
    return _map_geofence_response(updated)


@router.patch("/{geofence_id}/status", response_model=GeofenceResponse, summary="Enable or disable geofence (Admin only)")
def set_geofence_status(
    geofence_id: int,
    status_in: GeofenceStatusUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = GeofenceService(db)
    updated = service.set_geofence_status(geofence_id, status_in.is_active, user_id=current_admin.id)
    return _map_geofence_response(updated)


@router.delete("/{geofence_id}", response_model=StandardResponse[dict], summary="Delete a geofence (Admin only)")
def delete_geofence(
    geofence_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = GeofenceService(db)
    service.delete_geofence(geofence_id, user_id=current_admin.id)
    return StandardResponse(
        success=True,
        message=f"Geofence {geofence_id} deleted successfully",
        data={"id": geofence_id},
    )
