from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import select, func
from app.models.geofence import Geofence, GeofencePoint


class GeofenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, geofence_id: int) -> Optional[Geofence]:
        stmt = (
            select(Geofence)
            .options(selectinload(Geofence.points), joinedload(Geofence.creator))
            .where(Geofence.id == geofence_id)
        )
        return self.db.scalars(stmt).first()

    def get_all_active(self) -> List[Geofence]:
        stmt = (
            select(Geofence)
            .options(selectinload(Geofence.points))
            .where(Geofence.is_active == True)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, geofence: Geofence, points: Optional[List[GeofencePoint]] = None) -> Geofence:
        self.db.add(geofence)
        self.db.flush()

        if points and geofence.type == "POLYGON":
            for idx, pt in enumerate(points):
                pt.geofence_id = geofence.id
                pt.point_order = idx
                self.db.add(pt)

        self.db.commit()
        return self.get_by_id(geofence.id)  # type: ignore

    def update(
        self,
        geofence: Geofence,
        name: Optional[str] = None,
        description: Optional[str] = None,
        geo_type: Optional[str] = None,
        center_lat: Optional[float] = None,
        center_lon: Optional[float] = None,
        radius: Optional[float] = None,
        is_active: Optional[bool] = None,
        new_points: Optional[List[GeofencePoint]] = None,
    ) -> Geofence:
        if name is not None:
            geofence.name = name
        if description is not None:
            geofence.description = description
        if geo_type is not None:
            geofence.type = geo_type
        if center_lat is not None:
            geofence.center_latitude = center_lat
        if center_lon is not None:
            geofence.center_longitude = center_lon
        if radius is not None:
            geofence.radius_meters = radius
        if is_active is not None:
            geofence.is_active = is_active

        if new_points is not None and geofence.type == "POLYGON":
            # Remove old points
            for old_pt in list(geofence.points):
                self.db.delete(old_pt)
            self.db.flush()
            # Add updated points
            for idx, pt in enumerate(new_points):
                pt.geofence_id = geofence.id
                pt.point_order = idx
                self.db.add(pt)

        self.db.commit()
        return self.get_by_id(geofence.id)  # type: ignore

    def set_status(self, geofence: Geofence, is_active: bool) -> Geofence:
        geofence.is_active = is_active
        self.db.commit()
        self.db.refresh(geofence)
        return geofence

    def delete(self, geofence: Geofence) -> None:
        self.db.delete(geofence)
        self.db.commit()

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        geo_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Geofence], int]:
        stmt = select(Geofence).options(selectinload(Geofence.points), joinedload(Geofence.creator))
        count_stmt = select(func.count(Geofence.id))

        if search:
            search_filter = (Geofence.name.ilike(f"%{search}%")) | (Geofence.description.ilike(f"%{search}%"))
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if geo_type:
            stmt = stmt.where(Geofence.type == geo_type)
            count_stmt = count_stmt.where(Geofence.type == geo_type)

        if is_active is not None:
            stmt = stmt.where(Geofence.is_active == is_active)
            count_stmt = count_stmt.where(Geofence.is_active == is_active)

        total = self.db.scalar(count_stmt) or 0
        geofences = list(self.db.scalars(stmt.order_by(Geofence.id.desc()).offset(skip).limit(limit)).all())
        return geofences, total
