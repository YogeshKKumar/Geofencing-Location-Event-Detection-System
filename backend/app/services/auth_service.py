from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.repositories.audit_repository import AuditRepository
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def login(self, login_req: LoginRequest, ip_address: Optional[str] = None) -> TokenResponse:
        user = self.user_repo.get_by_email(login_req.email)
        if not user or not verify_password(login_req.password, user.password_hash):
            self.audit_repo.log(
                action="LOGIN_FAILED",
                entity_type="USER",
                new_value={"email": login_req.email},
                ip_address=ip_address,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact administrator.",
            )

        token = create_access_token(subject=user.id, role=user.role)
        self.audit_repo.log(
            action="LOGIN_SUCCESS",
            entity_type="USER",
            entity_id=user.id,
            user_id=user.id,
            ip_address=ip_address,
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    def register(self, reg_req: RegisterRequest, ip_address: Optional[str] = None) -> TokenResponse:
        existing = self.user_repo.get_by_email(reg_req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        new_user = User(
            name=reg_req.name,
            email=reg_req.email,
            password_hash=get_password_hash(reg_req.password),
            role="USER",
            is_active=True,
        )
        created_user = self.user_repo.create(new_user)

        self.audit_repo.log(
            action="REGISTER_USER",
            entity_type="USER",
            entity_id=created_user.id,
            user_id=created_user.id,
            new_value={"email": created_user.email, "role": created_user.role},
            ip_address=ip_address,
        )

        token = create_access_token(subject=created_user.id, role=created_user.role)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(created_user),
        )
