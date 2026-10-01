from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse, PaginationMetadata, StandardResponse
from app.schemas.device import DeviceResponse
from app.routers.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, summary="Create a new user (Admin only)")
def create_user(
    user_in: UserCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    user = service.create_user(user_in, admin_id=current_admin.id)
    return UserResponse.model_validate(user)


@router.get("", response_model=PaginatedResponse[UserResponse], summary="List users (Admin only)")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    skip = (page - 1) * page_size
    users, total = service.list_users(
        skip=skip, limit=page_size, search=search, role=role, is_active=is_active
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[UserResponse](
        success=True,
        data=[UserResponse.model_validate(u) for u in users],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Get user details by ID")
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' information",
        )
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse, summary="Update user by ID")
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other users' information",
        )
    service = UserService(db)
    # Non-admins cannot promote themselves to admin
    if current_user.role != "ADMIN" and user_in.role is not None and user_in.role != current_user.role:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change role without administrative privileges",
        )
    user = service.update_user(user_id, user_in, admin_id=current_user.id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/status", response_model=UserResponse, summary="Activate or deactivate a user (Admin only)")
def set_user_status(
    user_id: int,
    is_active: bool = Query(...),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    user = service.set_user_status(user_id, is_active, admin_id=current_admin.id)
    return UserResponse.model_validate(user)


@router.get("/{user_id}/devices", response_model=PaginatedResponse[DeviceResponse], summary="List devices owned by user")
def get_user_devices(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view another user's devices",
        )
    from app.services.device_service import DeviceService
    device_service = DeviceService(db)
    skip = (page - 1) * page_size
    devices, total = device_service.list_devices(skip=skip, limit=page_size, user_id=user_id)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[DeviceResponse](
        success=True,
        data=[
            DeviceResponse(
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
            for d in devices
        ],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )
