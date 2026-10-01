from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.repositories.audit_repository import AuditRepository
from app.models.audit_log import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)

    def list_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[List[AuditLog], int]:
        return self.audit_repo.list(
            skip=skip,
            limit=limit,
            action=action,
            entity_type=entity_type,
            user_id=user_id,
        )
