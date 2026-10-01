from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.event_repository import EventRepository
from app.models.geofence_event import GeofenceEvent


class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)

    def get_event_by_id(self, event_id: int) -> GeofenceEvent:
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Geofence event with ID {event_id} not found",
            )
        return event

    def list_events(
        self,
        skip: int = 0,
        limit: int = 50,
        device_id: Optional[int] = None,
        user_id: Optional[int] = None,
        geofence_id: Optional[int] = None,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[GeofenceEvent], int]:
        return self.event_repo.list(
            skip=skip,
            limit=limit,
            device_id=device_id,
            user_id=user_id,
            geofence_id=geofence_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )
