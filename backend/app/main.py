from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.routers import (
    auth_router,
    users_router,
    devices_router,
    geofences_router,
    locations_router,
    events_router,
    dashboard_router,
    audit_logs_router,
)

# Initialize application logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-Grade Geofencing & Location Event Detection System Backend with Circular & Polygon Geofences, Hysteresis, and Real-Time Event State Machine.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API Routers under /api and /api/v1
for prefix in [settings.API_V1_STR, "/api/v1"]:
    app.include_router(auth_router, prefix=prefix)
    app.include_router(users_router, prefix=prefix)
    app.include_router(devices_router, prefix=prefix)
    app.include_router(geofences_router, prefix=prefix)
    app.include_router(locations_router, prefix=prefix)
    app.include_router(events_router, prefix=prefix)
    app.include_router(dashboard_router, prefix=prefix)
    app.include_router(audit_logs_router, prefix=prefix)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": "ok",
    }
