from typing import List, Dict, Optional, Tuple, Any
from app.geofencing.circle import is_inside_circle
from app.geofencing.polygon import is_inside_polygon
from app.geofencing.state import determine_transition, GeofenceState
from app.core.config import settings
from app.models.geofence import Geofence


class GeofenceEvaluationResult:
    def __init__(
        self,
        geofence_id: int,
        geofence_name: str,
        previous_state: str,
        current_state: str,
        event_type: Optional[str] = None,
    ):
        self.geofence_id = geofence_id
        self.geofence_name = geofence_name
        self.previous_state = previous_state
        self.current_state = current_state
        self.event_type = event_type


class GeofencingEngine:
    def __init__(
        self,
        boundary_buffer: float = settings.BOUNDARY_BUFFER_METERS,
        accuracy_threshold: float = settings.GPS_ACCURACY_THRESHOLD,
        record_periodic_inside: bool = settings.RECORD_PERIODIC_INSIDE_EVENTS,
        record_periodic_outside: bool = settings.RECORD_PERIODIC_OUTSIDE_EVENTS,
    ):
        self.boundary_buffer = boundary_buffer
        self.accuracy_threshold = accuracy_threshold
        self.record_periodic_inside = record_periodic_inside
        self.record_periodic_outside = record_periodic_outside

    def evaluate_geofence(
        self,
        geofence: Geofence,
        latitude: float,
        longitude: float,
        accuracy_meters: float = 0.0,
        previous_state: str = GeofenceState.UNKNOWN.value,
    ) -> GeofenceEvaluationResult:
        """
        Evaluate a single geofence against a GPS coordinate.
        """
        is_inside = False

        if geofence.type == "CIRCLE":
            if geofence.center_latitude is not None and geofence.center_longitude is not None and geofence.radius_meters:
                is_inside = is_inside_circle(
                    point_lat=latitude,
                    point_lon=longitude,
                    center_lat=geofence.center_latitude,
                    center_lon=geofence.center_longitude,
                    radius_meters=geofence.radius_meters,
                    accuracy_meters=accuracy_meters,
                    previous_state=previous_state,
                    boundary_buffer=self.boundary_buffer,
                    accuracy_threshold=self.accuracy_threshold,
                )
        elif geofence.type == "POLYGON":
            poly_points = [(p.latitude, p.longitude) for p in sorted(geofence.points, key=lambda x: x.point_order)]
            if len(poly_points) >= 3:
                is_inside = is_inside_polygon(
                    point_lat=latitude,
                    point_lon=longitude,
                    polygon_points=poly_points,
                    accuracy_meters=accuracy_meters,
                    previous_state=previous_state,
                    boundary_buffer=self.boundary_buffer,
                    accuracy_threshold=self.accuracy_threshold,
                )

        current_state = GeofenceState.INSIDE.value if is_inside else GeofenceState.OUTSIDE.value

        event_type = determine_transition(
            previous_state=previous_state,
            current_state=current_state,
            record_periodic_inside=self.record_periodic_inside,
            record_periodic_outside=self.record_periodic_outside,
        )

        return GeofenceEvaluationResult(
            geofence_id=geofence.id,
            geofence_name=geofence.name,
            previous_state=previous_state,
            current_state=current_state,
            event_type=event_type,
        )

    def evaluate_all(
        self,
        geofences: List[Geofence],
        latitude: float,
        longitude: float,
        accuracy_meters: float = 0.0,
        previous_states: Optional[Dict[int, str]] = None,
    ) -> List[GeofenceEvaluationResult]:
        """
        Evaluate multiple active geofences simultaneously for a given coordinate.
        """
        if previous_states is None:
            previous_states = {}

        results: List[GeofenceEvaluationResult] = []
        for geofence in geofences:
            if not geofence.is_active:
                continue
            prev_state = previous_states.get(geofence.id, GeofenceState.UNKNOWN.value)
            eval_res = self.evaluate_geofence(
                geofence=geofence,
                latitude=latitude,
                longitude=longitude,
                accuracy_meters=accuracy_meters,
                previous_state=prev_state,
            )
            results.append(eval_res)

        return results


geofencing_engine = GeofencingEngine()
