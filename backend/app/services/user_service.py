from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.repositories.audit_repository import AuditRepository
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def create_user(self, user_in: UserCreate, admin_id: Optional[int] = None) -> User:
        existing = self.user_repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        new_user = User(
            name=user_in.name,
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            role=user_in.role,
            is_active=user_in.is_active,
        )
        created = self.user_repo.create(new_user)

        self.audit_repo.log(
            action="CREATE_USER",
            entity_type="USER",
            entity_id=created.id,
            user_id=admin_id,
            new_value={"name": created.name, "email": created.email, "role": created.role},
        )
        return created

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return user

    def update_user(self, user_id: int, user_in: UserUpdate, admin_id: Optional[int] = None) -> User:
        user = self.get_user_by_id(user_id)
        old_val = {"name": user.name, "email": user.email, "role": user.role, "is_active": user.is_active}

        if user_in.email and user_in.email != user.email:
            existing = self.user_repo.get_by_email(user_in.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email is already taken by another user",
                )
            user.email = user_in.email

        if user_in.name is not None:
            user.name = user_in.name
        if user_in.role is not None:
            user.role = user_in.role
        if user_in.is_active is not None:
            user.is_active = user_in.is_active
        if user_in.password is not None:
            user.password_hash = get_password_hash(user_in.password)

        updated = self.user_repo.update(user)

        self.audit_repo.log(
            action="UPDATE_USER",
            entity_type="USER",
            entity_id=updated.id,
            user_id=admin_id,
            old_value=old_val,
            new_value={"name": updated.name, "email": updated.email, "role": updated.role, "is_active": updated.is_active},
        )
        return updated

    def set_user_status(self, user_id: int, is_active: bool, admin_id: Optional[int] = None) -> User:
        user = self.get_user_by_id(user_id)
        user.is_active = is_active
        updated = self.user_repo.update(user)

        self.audit_repo.log(
            action="ENABLE_USER" if is_active else "DISABLE_USER",
            entity_type="USER",
            entity_id=updated.id,
            user_id=admin_id,
            new_value={"is_active": is_active},
        )
        return updated

    def list_users(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        return self.user_repo.list(skip=skip, limit=limit, search=search, role=role, is_active=is_active)
