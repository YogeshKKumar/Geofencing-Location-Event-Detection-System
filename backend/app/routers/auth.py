from typing import Optional
from fastapi import APIRouter, Depends, Request, Body, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, summary="Register a new user account")
def register(
    reg_in: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_addr = request.client.host if request.client else None
    service = AuthService(db)
    return service.register(reg_in, ip_address=ip_addr)


@router.post("/login", response_model=TokenResponse, summary="Log in with email and password")
async def login(
    request: Request,
    login_in: Optional[LoginRequest] = Body(None),
    db: Session = Depends(get_db),
):
    ip_addr = request.client.host if request.client else None
    service = AuthService(db)

    email = None
    password = None

    if login_in is not None:
        email = login_in.email
        password = login_in.password
    else:
        content_type = request.headers.get("content-type", "")
        if "form" in content_type:
            form = await request.form()
            email = form.get("email") or form.get("username")
            password = form.get("password")
        elif "application/json" in content_type:
            try:
                body = await request.json()
                email = body.get("email") or body.get("username")
                password = body.get("password")
            except Exception:
                pass

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    login_req = LoginRequest(email=email, password=password)
    return service.login(login_req, ip_address=ip_addr)


@router.post("/token", response_model=TokenResponse, summary="OAuth2 compatible login endpoint", include_in_schema=False)
def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    return service.login(LoginRequest(email=form_data.username, password=form_data.password))


@router.get("/me", response_model=UserResponse, summary="Get current authenticated user profile")
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
