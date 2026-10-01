from datetime import datetime, timezone, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from app.models.user import User
from app.models.device import Device
from app.models.geofence import Geofence
from app.models.geofence_event import GeofenceEvent
from app.repositories.event_repository import EventRepository
from app.schemas.dashboard import DashboardSummary, DeviceStatusSummary, GeofenceStatusSummary


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)

    def get_summary(self) -> DashboardSummary:
        total_users = self.db.scalar(select(func.count(User.id))) or 0
        total_devices = self.db.scalar(select(func.count(Device.id))) or 0
        active_devices = self.db.scalar(select(func.count(Device.id)).where(Device.is_active == True)) or 0
        active_geofences = self.db.scalar(select(func.count(Geofence.id)).where(Geofence.is_active == True)) or 0

        # Events today (UTC start of day)
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

        events_today = self.db.scalar(
            select(func.count(GeofenceEvent.id)).where(GeofenceEvent.timestamp >= today_start)
        ) or 0
        enter_events = self.db.scalar(
            select(func.count(GeofenceEvent.id)).where(
                and_(GeofenceEvent.timestamp >= today_start, GeofenceEvent.event_type == "ENTER")
            )
        ) or 0
        exit_events = self.db.scalar(
            select(func.count(GeofenceEvent.id)).where(
                and_(GeofenceEvent.timestamp >= today_start, GeofenceEvent.event_type == "EXIT")
            )
        ) or 0

        # Devices currently inside vs outside
        devices = self.db.scalars(select(Device)).all()
        devices_inside = 0
        devices_outside = 0

        for d in devices:
            latest_states = self.event_repo.get_latest_states_for_device(d.id)
            if any(st == "INSIDE" for st in latest_states.values()):
                devices_inside += 1
            else:
                devices_outside += 1

        return DashboardSummary(
            total_users=total_users,
            total_devices=total_devices,
            active_devices=active_devices,
            active_geofences=active_geofences,
            events_today=events_today,
            enter_events=enter_events,
            exit_events=exit_events,
            devices_currently_inside=devices_inside,
            devices_currently_outside=devices_outside,
        )

    def get_device_statuses(self) -> List[DeviceStatusSummary]:
        devices = self.db.scalars(select(Device).order_by(Device.name)).all()
        geofence_map = {g.id: g.name for g in self.db.scalars(select(Geofence)).all()}

        statuses: List[DeviceStatusSummary] = []
        for d in devices:
            latest_states = self.event_repo.get_latest_states_for_device(d.id)
            inside_geofence_names = [
                geofence_map[g_id]
                for g_id, state in latest_states.items()
                if state == "INSIDE" and g_id in geofence_map
            ]

            overall_state = "INSIDE" if inside_geofence_names else ("OUTSIDE" if d.last_location_at else "UNKNOWN")

            statuses.append(
                DeviceStatusSummary(
                    device_id=d.id,
                    device_name=d.name,
                    device_identifier=d.device_identifier,
                    is_active=d.is_active,
                    last_latitude=d.last_latitude,
                    last_longitude=d.last_longitude,
                    last_location_at=d.last_location_at,
                    user_name=d.user.name if d.user else None,
                    current_state=overall_state,
                    inside_geofences=inside_geofence_names,
                )
            )

        return statuses

    def get_geofence_statuses(self) -> List[GeofenceStatusSummary]:
        geofences = self.db.scalars(select(Geofence).order_by(Geofence.name)).all()
        devices = self.db.scalars(select(Device)).all()

        device_states: Dict[int, Dict[int, str]] = {}
        for d in devices:
            device_states[d.id] = self.event_repo.get_latest_states_for_device(d.id)

        device_name_map = {d.id: d.name for d in devices}

        statuses: List[GeofenceStatusSummary] = []
        for g in geofences:
            inside_devices: List[str] = []
            for d_id, states in device_states.items():
                if states.get(g.id) == "INSIDE":
                    inside_devices.append(device_name_map.get(d_id, f"Device {d_id}"))

            statuses.append(
                GeofenceStatusSummary(
                    geofence_id=g.id,
                    geofence_name=g.name,
                    type=g.type,
                    is_active=g.is_active,
                    current_device_count=len(inside_devices),
                    devices_inside=inside_devices,
                )
            )

        return statuses
