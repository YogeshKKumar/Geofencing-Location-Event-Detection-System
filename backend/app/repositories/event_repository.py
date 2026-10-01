from datetime import datetime
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_, desc
from app.models.geofence_event import GeofenceEvent
from app.models.geofence import Geofence
from app.models.device import Device
from app.models.user import User


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, event_id: int) -> Optional[GeofenceEvent]:
        stmt = (
            select(GeofenceEvent)
            .options(
                joinedload(GeofenceEvent.device),
                joinedload(GeofenceEvent.geofence),
                joinedload(GeofenceEvent.user),
            )
            .where(GeofenceEvent.id == event_id)
        )
        return self.db.scalars(stmt).first()

    def get_latest_states_for_device(self, device_id: int) -> Dict[int, str]:
        """
        Get the most recent current_state for all geofences evaluated for this device.
        Returns a dict: { geofence_id: current_state }.
        """
        # Subquery or ordered fetch
        stmt = (
            select(GeofenceEvent)
            .where(GeofenceEvent.device_id == device_id)
            .order_by(GeofenceEvent.timestamp.desc(), GeofenceEvent.id.desc())
        )
        events = self.db.scalars(stmt).all()

        latest_states: Dict[int, str] = {}
        for ev in events:
            if ev.geofence_id not in latest_states:
                latest_states[ev.geofence_id] = ev.current_state

        return latest_states

    def create(self, event: GeofenceEvent) -> GeofenceEvent:
        self.db.add(event)
        self.db.flush()
        return event

    def list(
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
        stmt = select(GeofenceEvent).options(
            joinedload(GeofenceEvent.device),
            joinedload(GeofenceEvent.geofence),
            joinedload(GeofenceEvent.user),
        )
        count_stmt = select(func.count(GeofenceEvent.id))

        filters = []
        if device_id:
            filters.append(GeofenceEvent.device_id == device_id)
        if user_id:
            filters.append(GeofenceEvent.user_id == user_id)
        if geofence_id:
            filters.append(GeofenceEvent.geofence_id == geofence_id)
        if event_type:
            filters.append(GeofenceEvent.event_type == event_type)
        if start_date:
            filters.append(GeofenceEvent.timestamp >= start_date)
        if end_date:
            filters.append(GeofenceEvent.timestamp <= end_date)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        total = self.db.scalar(count_stmt) or 0
        events = list(
            self.db.scalars(
                stmt.order_by(GeofenceEvent.timestamp.desc(), GeofenceEvent.id.desc()).offset(skip).limit(limit)
            ).all()
        )
        return events, total
