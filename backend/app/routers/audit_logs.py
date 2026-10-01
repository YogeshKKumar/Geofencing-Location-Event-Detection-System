from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.audit_service import AuditService
from app.schemas.audit_log import AuditLogResponse
from app.schemas.common import PaginatedResponse, PaginationMetadata
from app.routers.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


def _map_audit_response(a) -> AuditLogResponse:
    return AuditLogResponse(
        id=a.id,
        user_id=a.user_id,
        user_name=a.user.name if a.user else None,
        action=a.action,
        entity_type=a.entity_type,
        entity_id=a.entity_id,
        old_value=a.old_value,
        new_value=a.new_value,
        ip_address=a.ip_address,
        created_at=a.created_at,
    )


@router.get("", response_model=PaginatedResponse[AuditLogResponse], summary="List system audit logs (Admin only)")
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AuditService(db)
    skip = (page - 1) * page_size
    logs, total = service.list_logs(
        skip=skip,
        limit=page_size,
        action=action,
        entity_type=entity_type,
        user_id=user_id,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[AuditLogResponse](
        success=True,
        data=[_map_audit_response(l) for l in logs],
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )
