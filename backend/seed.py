from datetime import datetime, timezone, timedelta
from app.database.session import SessionLocal
from app.models.user import User
from app.models.device import Device
from app.models.geofence import Geofence, GeofencePoint
from app.models.location_event import LocationEvent
from app.models.geofence_event import GeofenceEvent
from app.models.audit_log import AuditLog
from app.core.security import get_password_hash


def seed_database():
    db = SessionLocal()
    try:
        print("[SEED] Seeding database with demo data...")

        # 1. Admin & Users
        admin_email = "admin@example.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name="System Administrator",
                email=admin_email,
                password_hash=get_password_hash("Admin@123"),
                role="ADMIN",
                is_active=True,
            )
            db.add(admin)
            db.flush()
            print(f"Created Admin: {admin_email} / Admin@123")

        user1_email = "user1@example.com"
        user1 = db.query(User).filter(User.email == user1_email).first()
        if not user1:
            user1 = User(
                name="John Logistics",
                email=user1_email,
                password_hash=get_password_hash("User1@123"),
                role="USER",
                is_active=True,
            )
            db.add(user1)
            db.flush()
            print(f"Created User: {user1_email} / User1@123")

        user2_email = "user2@example.com"
        user2 = db.query(User).filter(User.email == user2_email).first()
        if not user2:
            user2 = User(
                name="Sarah FieldTech",
                email=user2_email,
                password_hash=get_password_hash("User2@123"),
                role="USER",
                is_active=True,
            )
            db.add(user2)
            db.flush()
            print(f"Created User: {user2_email} / User2@123")

        # 2. Devices
        dev1 = db.query(Device).filter(Device.device_identifier == "DEVICE-001").first()
        if not dev1:
            dev1 = Device(
                device_identifier="DEVICE-001",
                name="Delivery Van Alpha",
                user_id=user1.id,
                is_active=True,
                last_latitude=11.0169,
                last_longitude=76.9559,
                last_location_at=datetime.now(timezone.utc),
            )
            db.add(dev1)
            db.flush()
            print("Created Device: DEVICE-001")

        dev2 = db.query(Device).filter(Device.device_identifier == "DEVICE-002").first()
        if not dev2:
            dev2 = Device(
                device_identifier="DEVICE-002",
                name="Field Technician Beta",
                user_id=user2.id,
                is_active=True,
                last_latitude=11.0250,
                last_longitude=76.9650,
                last_location_at=datetime.now(timezone.utc),
            )
            db.add(dev2)
            db.flush()
            print("Created Device: DEVICE-002")

        dev3 = db.query(Device).filter(Device.device_identifier == "DEVICE-003").first()
        if not dev3:
            dev3 = Device(
                device_identifier="DEVICE-003",
                name="Security Patrol Drone",
                user_id=user1.id,
                is_active=True,
                last_latitude=11.0165,
                last_longitude=76.9560,
                last_location_at=datetime.now(timezone.utc),
            )
            db.add(dev3)
            db.flush()
            print("Created Device: DEVICE-003")

        # 3. Geofences
        geo_office = db.query(Geofence).filter(Geofence.name == "Office Circle").first()
        if not geo_office:
            geo_office = Geofence(
                name="Office Circle",
                description="Main headquarters compound boundary",
                type="CIRCLE",
                center_latitude=11.0168,
                center_longitude=76.9558,
                radius_meters=500.0,
                is_active=True,
                created_by=admin.id,
            )
            db.add(geo_office)
            db.flush()
            print("Created Geofence: Office Circle")

        geo_warehouse = db.query(Geofence).filter(Geofence.name == "Warehouse Polygon").first()
        if not geo_warehouse:
            geo_warehouse = Geofence(
                name="Warehouse Polygon",
                description="Secure central logistics depot zone",
                type="POLYGON",
                is_active=True,
                created_by=admin.id,
            )
            db.add(geo_warehouse)
            db.flush()

            poly_pts = [
                GeofencePoint(geofence_id=geo_warehouse.id, latitude=11.0160, longitude=76.9550, point_order=0),
                GeofencePoint(geofence_id=geo_warehouse.id, latitude=11.0175, longitude=76.9550, point_order=1),
                GeofencePoint(geofence_id=geo_warehouse.id, latitude=11.0175, longitude=76.9575, point_order=2),
                GeofencePoint(geofence_id=geo_warehouse.id, latitude=11.0160, longitude=76.9575, point_order=3),
            ]
            db.add_all(poly_pts)
            print("Created Geofence: Warehouse Polygon")

        geo_parking = db.query(Geofence).filter(Geofence.name == "Parking Area Circle").first()
        if not geo_parking:
            geo_parking = Geofence(
                name="Parking Area Circle",
                description="Fleet parking and charging bay",
                type="CIRCLE",
                center_latitude=11.0180,
                center_longitude=76.9560,
                radius_meters=200.0,
                is_active=True,
                created_by=admin.id,
            )
            db.add(geo_parking)
            db.flush()
            print("Created Geofence: Parking Area Circle")

        # 4. Initial Location & Events for Demo
        if db.query(LocationEvent).count() == 0:
            now = datetime.now(timezone.utc)
            loc1 = LocationEvent(
                device_id=dev1.id,
                user_id=dev1.user_id,
                latitude=11.0169,
                longitude=76.9559,
                accuracy_meters=5.0,
                timestamp=now - timedelta(minutes=15),
            )
            db.add(loc1)
            db.flush()

            ev1 = GeofenceEvent(
                device_id=dev1.id,
                user_id=dev1.user_id,
                geofence_id=geo_office.id,
                location_event_id=loc1.id,
                event_type="ENTER",
                previous_state="OUTSIDE",
                current_state="INSIDE",
                latitude=11.0169,
                longitude=76.9559,
                accuracy_meters=5.0,
                timestamp=now - timedelta(minutes=15),
            )
            db.add(ev1)

            ev2 = GeofenceEvent(
                device_id=dev1.id,
                user_id=dev1.user_id,
                geofence_id=geo_warehouse.id,
                location_event_id=loc1.id,
                event_type="ENTER",
                previous_state="OUTSIDE",
                current_state="INSIDE",
                latitude=11.0169,
                longitude=76.9559,
                accuracy_meters=5.0,
                timestamp=now - timedelta(minutes=15),
            )
            db.add(ev2)

            # Audit log
            audit = AuditLog(
                action="SYSTEM_INIT",
                entity_type="SYSTEM",
                entity_id=None,
                user_id=admin.id,
                new_value={"message": "System seeded with initial baseline demo data"},
            )
            db.add(audit)

        db.commit()
        print("[SUCCESS] Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
