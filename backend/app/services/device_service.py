from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.device_repository import DeviceRepository
from app.repositories.user_repository import UserRepository
from app.repositories.audit_repository import AuditRepository
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceService:
    def __init__(self, db: Session):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def create_device(self, device_in: DeviceCreate, user_id: Optional[int] = None) -> Device:
        existing = self.device_repo.get_by_identifier(device_in.device_identifier)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device identifier '{device_in.device_identifier}' already exists",
            )

        if device_in.user_id:
            assigned_user = self.user_repo.get_by_id(device_in.user_id)
            if not assigned_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Assigned user with ID {device_in.user_id} not found",
                )

        new_device = Device(
            device_identifier=device_in.device_identifier,
            name=device_in.name,
            user_id=device_in.user_id,
            is_active=device_in.is_active,
        )
        created = self.device_repo.create(new_device)

        self.audit_repo.log(
            action="CREATE_DEVICE",
            entity_type="DEVICE",
            entity_id=created.id,
            user_id=user_id,
            new_value={"identifier": created.device_identifier, "name": created.name, "user_id": created.user_id},
        )
        return created

    def get_device_by_id(self, device_id: int) -> Device:
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {device_id} not found",
            )
        return device

    def update_device(self, device_id: int, device_in: DeviceUpdate, user_id: Optional[int] = None) -> Device:
        device = self.get_device_by_id(device_id)
        old_val = {"name": device.name, "user_id": device.user_id, "is_active": device.is_active}

        if device_in.user_id is not None:
            if device_in.user_id > 0:
                assigned_user = self.user_repo.get_by_id(device_in.user_id)
                if not assigned_user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Assigned user with ID {device_in.user_id} not found",
                    )
                device.user_id = device_in.user_id
            else:
                device.user_id = None

        if device_in.name is not None:
            device.name = device_in.name
        if device_in.is_active is not None:
            device.is_active = device_in.is_active

        updated = self.device_repo.update(device)

        self.audit_repo.log(
            action="UPDATE_DEVICE",
            entity_type="DEVICE",
            entity_id=updated.id,
            user_id=user_id,
            old_value=old_val,
            new_value={"name": updated.name, "user_id": updated.user_id, "is_active": updated.is_active},
        )
        return updated

    def set_device_status(self, device_id: int, is_active: bool, user_id: Optional[int] = None) -> Device:
        device = self.get_device_by_id(device_id)
        device.is_active = is_active
        updated = self.device_repo.update(device)

        self.audit_repo.log(
            action="ENABLE_DEVICE" if is_active else "DISABLE_DEVICE",
            entity_type="DEVICE",
            entity_id=updated.id,
            user_id=user_id,
            new_value={"is_active": is_active},
        )
        return updated

    def delete_device(self, device_id: int, user_id: Optional[int] = None) -> None:
        device = self.get_device_by_id(device_id)
        self.device_repo.delete(device)

        self.audit_repo.log(
            action="DELETE_DEVICE",
            entity_type="DEVICE",
            entity_id=device_id,
            user_id=user_id,
            old_value={"identifier": device.device_identifier, "name": device.name},
        )

    def list_devices(
        self,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Device], int]:
        return self.device_repo.list(
            skip=skip, limit=limit, user_id=user_id, is_active=is_active, search=search
        )
