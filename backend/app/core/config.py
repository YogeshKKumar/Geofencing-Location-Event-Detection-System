from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Geofencing & Location Event Detection System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = "mysql+pymysql://geofence_user:geofence_password@localhost:3306/geofencing_db"

    # JWT Security
    JWT_SECRET_KEY: str = "9e5c46e082bcfb4012bc051c518778be1b702ec4087140f75e2ef75f6e625574"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for development ease

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    # Geofencing Engine Configuration
    GPS_ACCURACY_THRESHOLD: float = 100.0  # Max accuracy radius (meters) before discarding or flagging
    BOUNDARY_BUFFER_METERS: float = 10.0  # Hysteresis buffer to prevent edge oscillation
    STATE_CONFIRMATION_COUNT: int = 1     # Consecutive readings required for transition
    RECORD_PERIODIC_INSIDE_EVENTS: bool = True   # Record INSIDE events for repeated location checks
    RECORD_PERIODIC_OUTSIDE_EVENTS: bool = False # Record OUTSIDE events for repeated outside checks
    DUPLICATE_INTERVAL_SECONDS: int = 5   # Discard identical GPS within this time window


settings = Settings()
