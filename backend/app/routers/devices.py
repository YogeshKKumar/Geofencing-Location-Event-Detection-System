from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.device_service import DeviceService
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceStatusUpdate, DeviceResponse
from app.schemas.common import PaginatedResponse, PaginationMetadata, StandardResponse
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/devices", tags=["Devices"])


def _map_device_response(d) -> DeviceResponse:
    return DeviceResponse(
        id=d.id,
        device_identifier=d.device_identifier,
        name=d.name,
        user_id=d.user_id,
        is_active=d.is_active,
        last_latitude=d.last_latitude,
        last_longitude=d.last_longitude,
        last_location_at=d.last_location_at,
        created_at=d.created_at,
        updated_at=d.updated_at,
        user_name=d.user.name if d.user else None,
    )


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, summary="Register a new device")
def create_device(
    device_in: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DeviceService(db)
    # If standard user, auto-assign device to themselves if not specified
    if current_user.role != "ADMIN" and not device_in.user_id:
        device_in.user_id = current_user.id
    created = service.create_device(device_in, user_id=current_user.id)
    return _map_device_response(created)


@router.get("", response_model=PaginatedResponse[DeviceResponse], summary="List registered devices")
def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DeviceService(db)
    target_user_id = user_id
    if current_user.role != "ADMIN":
        target_user_id = current_user.id

    skip = (page - 1) * page_size
    devices, total = service.list_devices(
        skip=skip,
        limit=page_size,
        user_id=target_user_id,
        is_active=is_active,
        search=search,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[DeviceResponse](
        success=True,
        data=[_map_device_response(d) for d in devices],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{device_id}", response_model=DeviceResponse, summary="Get device by ID")
def get_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DeviceService(db)
    device = service.get_device_by_id(device_id)
    if current_user.role != "ADMIN" and device.user_id != current_user.id:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Cannot view devices belonging to another user",
        )
    return _map_device_response(device)


@router.put("/{device_id}", response_model=DeviceResponse, summary="Update device details")
def update_device(
    device_id: int,
    device_in: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DeviceService(db)
    device = service.get_device_by_id(device_id)
    if current_user.role != "ADMIN" and device.user_id != current_user.id:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Cannot modify devices belonging to another user",
        )
    updated = service.update_device(device_id, device_in, user_id=current_user.id)
    return _map_device_response(updated)


@router.patch("/{device_id}/status", response_model=DeviceResponse, summary="Activate or deactivate a device")
def set_device_status(
    device_id: int,
    status_in: DeviceStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DeviceService(db)
    device = service.get_device_by_id(device_id)
    if current_user.role != "ADMIN" and device.user_id != current_user.id:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Cannot change status of devices belonging to another user",
        )
    updated = service.set_device_status(device_id, status_in.is_active, user_id=current_user.id)
    return _map_device_response(updated)


@router.delete("/{device_id}", response_model=StandardResponse[dict], summary="Delete a device")
def delete_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DeviceService(db)
    device = service.get_device_by_id(device_id)
    if current_user.role != "ADMIN" and device.user_id != current_user.id:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Cannot delete devices belonging to another user",
        )
    service.delete_device(device_id, user_id=current_user.id)
    return StandardResponse(success=True, message=f"Device {device_id} deleted successfully", data={"id": device_id})
