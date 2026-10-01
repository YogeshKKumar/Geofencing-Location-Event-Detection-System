from datetime import datetime
from typing import Optional, List, Tuple, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_
from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        audit_entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
        )
        self.db.add(audit_entry)
        self.db.commit()
        self.db.refresh(audit_entry)
        return audit_entry

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[List[AuditLog], int]:
        stmt = select(AuditLog).options(joinedload(AuditLog.user))
        count_stmt = select(func.count(AuditLog.id))

        filters = []
        if action:
            filters.append(AuditLog.action == action)
        if entity_type:
            filters.append(AuditLog.entity_type == entity_type)
        if user_id:
            filters.append(AuditLog.user_id == user_id)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        total = self.db.scalar(count_stmt) or 0
        logs = list(
            self.db.scalars(
                stmt.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).offset(skip).limit(limit)
            ).all()
        )
        return logs, total
