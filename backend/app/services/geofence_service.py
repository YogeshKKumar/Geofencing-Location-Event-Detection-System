from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.geofence_repository import GeofenceRepository
from app.repositories.audit_repository import AuditRepository
from app.models.geofence import Geofence, GeofencePoint
from app.schemas.geofence import GeofenceCreate, GeofenceUpdate

try:
    from shapely.geometry import Polygon
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


class GeofenceService:
    def __init__(self, db: Session):
        self.db = db
        self.geofence_repo = GeofenceRepository(db)
        self.audit_repo = AuditRepository(db)

    def validate_polygon_geometry(self, points: List[dict]):
        if len(points) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Polygon must contain at least 3 points",
            )
        if HAS_SHAPELY:
            try:
                poly = Polygon([(p["longitude"], p["latitude"]) for p in points])
                if not poly.is_valid:
                    # Try to see if it's self-intersecting
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Polygon points form an invalid or self-intersecting polygon",
                    )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid polygon geometry: {str(e)}",
                )

    def create_geofence(self, geo_in: GeofenceCreate, user_id: Optional[int] = None) -> Geofence:
        if geo_in.type == "CIRCLE":
            if geo_in.center_latitude is None or geo_in.center_longitude is None or not geo_in.radius_meters:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Circle geofence requires center_latitude, center_longitude, and radius_meters > 0",
                )
            new_geo = Geofence(
                name=geo_in.name,
                description=geo_in.description,
                type="CIRCLE",
                center_latitude=geo_in.center_latitude,
                center_longitude=geo_in.center_longitude,
                radius_meters=geo_in.radius_meters,
                is_active=geo_in.is_active,
                created_by=user_id,
            )
            created = self.geofence_repo.create(new_geo)
        elif geo_in.type == "POLYGON":
            if not geo_in.points or len(geo_in.points) < 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Polygon geofence requires at least 3 points",
                )
            points_data = [{"latitude": p.latitude, "longitude": p.longitude} for p in geo_in.points]
            self.validate_polygon_geometry(points_data)

            new_geo = Geofence(
                name=geo_in.name,
                description=geo_in.description,
                type="POLYGON",
                is_active=geo_in.is_active,
                created_by=user_id,
            )
            pts = [
                GeofencePoint(latitude=p.latitude, longitude=p.longitude, point_order=idx)
                for idx, p in enumerate(geo_in.points)
            ]
            created = self.geofence_repo.create(new_geo, points=pts)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported geofence type '{geo_in.type}'",
            )

        self.audit_repo.log(
            action="CREATE_GEOFENCE",
            entity_type="GEOFENCE",
            entity_id=created.id,
            user_id=user_id,
            new_value={"name": created.name, "type": created.type, "is_active": created.is_active},
        )
        return created

    def get_geofence_by_id(self, geofence_id: int) -> Geofence:
        geo = self.geofence_repo.get_by_id(geofence_id)
        if not geo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Geofence with ID {geofence_id} not found",
            )
        return geo

    def update_geofence(self, geofence_id: int, geo_in: GeofenceUpdate, user_id: Optional[int] = None) -> Geofence:
        geo = self.get_geofence_by_id(geofence_id)
        old_val = {
            "name": geo.name,
            "type": geo.type,
            "center_latitude": geo.center_latitude,
            "center_longitude": geo.center_longitude,
            "radius_meters": geo.radius_meters,
            "is_active": geo.is_active,
        }

        target_type = geo_in.type or geo.type
        pts = None
        if target_type == "POLYGON" and geo_in.points is not None:
            if len(geo_in.points) < 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Polygon geofence requires at least 3 points",
                )
            points_data = [{"latitude": p.latitude, "longitude": p.longitude} for p in geo_in.points]
            self.validate_polygon_geometry(points_data)
            pts = [
                GeofencePoint(latitude=p.latitude, longitude=p.longitude, point_order=idx)
                for idx, p in enumerate(geo_in.points)
            ]

        updated = self.geofence_repo.update(
            geofence=geo,
            name=geo_in.name,
            description=geo_in.description,
            geo_type=geo_in.type,
            center_lat=geo_in.center_latitude,
            center_lon=geo_in.center_longitude,
            radius=geo_in.radius_meters,
            is_active=geo_in.is_active,
            new_points=pts,
        )

        self.audit_repo.log(
            action="UPDATE_GEOFENCE",
            entity_type="GEOFENCE",
            entity_id=updated.id,
            user_id=user_id,
            old_value=old_val,
            new_value={"name": updated.name, "type": updated.type, "is_active": updated.is_active},
        )
        return updated

    def set_geofence_status(self, geofence_id: int, is_active: bool, user_id: Optional[int] = None) -> Geofence:
        geo = self.get_geofence_by_id(geofence_id)
        updated = self.geofence_repo.set_status(geo, is_active)

        self.audit_repo.log(
            action="ENABLE_GEOFENCE" if is_active else "DISABLE_GEOFENCE",
            entity_type="GEOFENCE",
            entity_id=updated.id,
            user_id=user_id,
            new_value={"is_active": is_active},
        )
        return updated

    def delete_geofence(self, geofence_id: int, user_id: Optional[int] = None) -> None:
        geo = self.get_geofence_by_id(geofence_id)
        self.geofence_repo.delete(geo)

        self.audit_repo.log(
            action="DELETE_GEOFENCE",
            entity_type="GEOFENCE",
            entity_id=geofence_id,
            user_id=user_id,
            old_value={"name": geo.name, "type": geo.type},
        )

    def list_geofences(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        geo_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Geofence], int]:
        return self.geofence_repo.list(
            skip=skip, limit=limit, search=search, geo_type=geo_type, is_active=is_active
        )
