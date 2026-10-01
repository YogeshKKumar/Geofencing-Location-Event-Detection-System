from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.device_repository import DeviceRepository
from app.repositories.geofence_repository import GeofenceRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.event_repository import EventRepository
from app.repositories.audit_repository import AuditRepository
from app.geofencing.engine import geofencing_engine, GeofenceEvaluationResult
from app.models.location_event import LocationEvent
from app.models.geofence_event import GeofenceEvent
from app.schemas.location import LocationInput, LocationProcessResponse, LocationEventTransition
from app.core.config import settings


class LocationService:
    def __init__(self, db: Session):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.geofence_repo = GeofenceRepository(db)
        self.location_repo = LocationRepository(db)
        self.event_repo = EventRepository(db)
        self.audit_repo = AuditRepository(db)

    def process_location(
        self,
        location_in: LocationInput,
        idempotency_key: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> LocationProcessResponse:
        """
        Transactional, concurrency-safe location ingestion and geofence event detection.
        """
        # 1. Lock and validate device
        device = self.device_repo.get_for_update(location_in.device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {location_in.device_id} not found",
            )

        if not device.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device '{device.name}' is inactive and cannot ingest locations",
            )

        timestamp = location_in.timestamp or datetime.now(timezone.utc)

        # 2. Duplicate prevention within time window
        is_dup = self.location_repo.check_duplicate(
            device_id=device.id,
            latitude=location_in.latitude,
            longitude=location_in.longitude,
            timestamp=timestamp,
            window_seconds=settings.DUPLICATE_INTERVAL_SECONDS,
        )
        if is_dup:
            latest_loc = self.location_repo.get_latest_by_device(device.id)
            return LocationProcessResponse(
                location_id=latest_loc.id if latest_loc else 0,
                device_id=device.id,
                events=[],
            )

        # 3. Create and persist LocationEvent
        loc_record = LocationEvent(
            device_id=device.id,
            user_id=device.user_id,
            latitude=location_in.latitude,
            longitude=location_in.longitude,
            accuracy_meters=location_in.accuracy_meters,
            timestamp=timestamp,
        )
        self.location_repo.create(loc_record)

        # 4. Update device's latest position
        device.last_latitude = location_in.latitude
        device.last_longitude = location_in.longitude
        device.last_location_at = timestamp
        self.db.flush()

        # 5. Retrieve active geofences & previous states for this device
        active_geofences = self.geofence_repo.get_all_active()
        previous_states = self.event_repo.get_latest_states_for_device(device.id)

        # 6. Run Geofencing Engine
        eval_results: List[GeofenceEvaluationResult] = geofencing_engine.evaluate_all(
            geofences=active_geofences,
            latitude=location_in.latitude,
            longitude=location_in.longitude,
            accuracy_meters=location_in.accuracy_meters,
            previous_states=previous_states,
        )

        detected_transitions: List[LocationEventTransition] = []

        # 7. Persist generated geofence events
        for res in eval_results:
            if res.event_type is not None:
                geo_event = GeofenceEvent(
                    device_id=device.id,
                    user_id=device.user_id,
                    geofence_id=res.geofence_id,
                    location_event_id=loc_record.id,
                    event_type=res.event_type,
                    previous_state=res.previous_state,
                    current_state=res.current_state,
                    latitude=location_in.latitude,
                    longitude=location_in.longitude,
                    accuracy_meters=location_in.accuracy_meters,
                    timestamp=timestamp,
                )
                self.event_repo.create(geo_event)

                detected_transitions.append(
                    LocationEventTransition(
                        geofence_id=res.geofence_id,
                        geofence_name=res.geofence_name,
                        event_type=res.event_type,
                        previous_state=res.previous_state,
                        current_state=res.current_state,
                    )
                )

        # 8. Commit entire transaction
        self.db.commit()
        self.db.refresh(loc_record)

        # 9. Audit log
        if detected_transitions:
            self.audit_repo.log(
                action="EVENT_GENERATED",
                entity_type="LOCATION_EVENT",
                entity_id=loc_record.id,
                user_id=device.user_id,
                new_value={
                    "device_id": device.id,
                    "event_count": len(detected_transitions),
                    "transitions": [t.model_dump() for t in detected_transitions],
                },
                ip_address=ip_address,
            )

        return LocationProcessResponse(
            location_id=loc_record.id,
            device_id=device.id,
            events=detected_transitions,
        )

    def list_locations(
        self,
        skip: int = 0,
        limit: int = 50,
        device_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[LocationEvent], int]:
        return self.location_repo.list(
            skip=skip,
            limit=limit,
            device_id=device_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
