# Geofencing & Location Event Detection System

A production-grade, full-stack spatial tracking and geofencing platform built with **FastAPI**, **React + TypeScript**, **MySQL**, **SQLAlchemy ORM**, **Alembic**, and **Leaflet / OpenStreetMap**.

This system supports real-time high-throughput GPS location ingestion, high-precision circular and arbitrary polygonal geofencing, GPS accuracy filtering, perimeter hysteresis debouncing, duplicate position suppression, deterministic state transitions (`ENTER`, `EXIT`, `INSIDE`, `OUTSIDE`), audit trails, and interactive maps.

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Geofencing Engine & Spatial Mathematics](#geofencing-engine--spatial-mathematics)
   - [Circular Geofence Evaluation (Haversine Formula)](#circular-geofence-evaluation)
   - [Polygonal Geofence Evaluation (Ray Casting & GEOS)](#polygonal-geofence-evaluation)
   - [Noise Filtering, Hysteresis, and Debouncing](#noise-filtering-hysteresis-and-debouncing)
3. [State Machine Transition Matrix](#state-machine-transition-matrix)
4. [Database Schema & Entity Relationships](#database-schema--entity-relationships)
5. [API Specification & cURL Examples](#api-specification--curl-examples)
6. [Frontend UI & Real-Time Visualization](#frontend-ui--real-time-visualization)
7. [Installation & Setup](#installation--setup)
   - [Option A: Docker Compose (Recommended)](#option-a-docker-compose-recommended)
   - [Option B: Local Manual Setup](#option-b-local-manual-setup)
8. [Seed Data & Demo Credentials](#seed-data--demo-credentials)
9. [Automated Testing Suite](#automated-testing-suite)
10. [Postman Collection](#postman-collection)

---

## System Architecture

```
                                  +-------------------------------------------------+
                                  |            React + TypeScript Frontend          |
                                  |  (MUI v9, Vite, React-Leaflet, OSM, Recharts)   |
                                  +-----------------------+-------------------------+
                                                          |
                                                          | HTTP REST / JSON
                                                          v
                                  +-------------------------------------------------+
                                  |              FastAPI Backend Gateway            |
                                  |     (CORS, JWT Bearer Auth, Request Logging)    |
                                  +-----------------------+-------------------------+
                                                          |
                 +----------------------------------------+----------------------------------------+
                 |                                        |                                        |
                 v                                        v                                        v
+---------------------------------+      +---------------------------------+      +---------------------------------+
|       Routers & Endpoints       |      |       Core Geofencing Engine    |      |       Repository / ORM Layer    |
| /auth, /devices, /geofences,    | ---> | - Haversine Circular Evaluator  | ---> | - SQLAlchemy 2.0 Async-ready    |
| /locations, /events, /dashboard |      | - Shapely/Ray-Casting Polygon   |      | - PyMySQL Driver                |
| /users, /audit-logs             |      | - Hysteresis & Accuracy Filter  |      | - Alembic Database Migrations   |
+---------------------------------+      | - State Transition Determiner   |      +----------------+----------------+
                                         +---------------------------------+                       |
                                                                                                   v
                                                                                  +---------------------------------+
                                                                                  |          MySQL 8.0 Engine       |
                                                                                  |   (Relational Schema & Audits)  |
                                                                                  +---------------------------------+
```

### Architectural Principles
- **Separation of Concerns**: Clean layered hierarchy: `Routers` $\rightarrow$ `Services` $\rightarrow$ `Repositories` $\rightarrow$ `Models`.
- **Pure Geofencing Core**: The spatial math engine in `app/geofencing/` is decoupled from database models and web framework code, enabling blazing fast, isolated unit testing.
- **Fail-Safe Fallbacks**: Polygon containment leverages C-optimized `Shapely` (GEOS) when available, and gracefully falls back to an internal pure-Python Ray-Casting algorithm.
- **Audit & Compliance**: All critical administrative mutations (geofence create/delete, device registration) and transitions are logged with JSON diffs in the `audit_logs` table.

---

## Geofencing Engine & Spatial Mathematics

### Circular Geofence Evaluation
Circular boundaries are defined by a center coordinate $(\phi_1, \lambda_1)$ and a radius $R$ in meters. The great-circle distance $d$ between the device location $(\phi_2, \lambda_2)$ and the circle center is calculated using the **Haversine formula**:

$$\Delta\phi = \phi_2 - \phi_1, \quad \Delta\lambda = \lambda_2 - \lambda_1$$

$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$

$$c = 2 \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$

$$d = R_{\text{earth}} \cdot c \quad \text{where } R_{\text{earth}} = 6,371,000 \text{ meters}$$

### Polygonal Geofence Evaluation
Arbitrary polygonal boundaries are defined by an ordered list of $N$ vertices $[(lat_0, lon_0), \dots, (lat_{N-1}, lon_{N-1})]$.

1. **Containment (Jordan Curve Theorem / Ray Casting)**:
   A horizontal ray is cast from the test point eastward to infinity. The number of intersections between the ray and the polygon edges is counted:
   - If the intersection count is **odd**, the coordinate lies **INSIDE**.
   - If the intersection count is **even**, the coordinate lies **OUTSIDE**.
2. **Boundary Proximity (Minimum Distance to Perimeter)**:
   For hysteresis calculations, the perpendicular distance from the test coordinate to every polygon line segment is evaluated using projection onto segments:
   $$t = \operatorname{clamp}\left(\frac{(P - A) \cdot (B - A)}{\|B - A\|^2}, 0, 1\right)$$
   $$\text{Closest Point } Q = A + t(B - A)$$
   $$d = \operatorname{Haversine}(P, Q)$$

### Noise Filtering, Hysteresis, and Debouncing

```
                                  [ Incoming GPS Fix ]
                                            |
                                            v
                                  { Duplicate Check }
                                (Same coord within 5s?)
                                       /         \
                                    YES           NO
                                     |             |
                                  [ Drop ]         v
                                        { Accuracy Check }
                                      (accuracy > 100m?)
                                             /         \
                                          YES           NO
                                           |             |
                              [ Retain Previous State ]  v
                                              { Boundary Evaluation }
                                             (Circle / Polygon Test)
                                                         |
                                                         v
                                              { Apply Hysteresis }
                                   (If inside, must exceed border + 10m to EXIT)
                                                         |
                                                         v
                                              [ Determine Transition ]
```

1. **GPS Accuracy Filtering**: GPS fixes with `accuracy_meters > 100.0m` are deemed unreliable. The engine retains the device's prior boundary state to prevent spurious alerts during satellite loss.
2. **Hysteresis Buffer (10.0m)**:
   - To transition from `OUTSIDE` $\rightarrow$ `INSIDE`: The coordinate must be strictly inside ($d \le R$).
   - To transition from `INSIDE` $\rightarrow$ `OUTSIDE`: The coordinate must move past the boundary by more than the hysteresis buffer ($d > R + 10\text{m}$).
3. **Temporal Deduplication**: Ingestion packets from the same device with identical latitude and longitude received within 5 seconds are safely suppressed.

---

## State Machine Transition Matrix

The engine maintains a per-device, per-geofence state machine:

| Previous State | Current Evaluated Position | Generated Event | Resulting State | Description |
| :--- | :--- | :--- | :--- | :--- |
| `UNKNOWN` | Inside boundary | `ENTER` | `INSIDE` | Device first detected inside geofence |
| `UNKNOWN` | Outside boundary | `OUTSIDE` | `OUTSIDE` | Initial discovery fix outside perimeter |
| `OUTSIDE` | Inside boundary | `ENTER` | `INSIDE` | Device crossed into geofence |
| `OUTSIDE` | Outside boundary | *(None)* | `OUTSIDE` | Device remains outside; no duplicate noise |
| `INSIDE` | Outside boundary ($> R + \text{buffer}$) | `EXIT` | `OUTSIDE` | Device crossed out of geofence |
| `INSIDE` | Inside boundary | `INSIDE` | `INSIDE` | Steady-state heartbeat fix inside zone |

---

## Database Schema & Entity Relationships

The relational model is managed via SQLAlchemy and version-controlled Alembic migrations:

```
+--------------------+        +--------------------+        +-----------------------+
|       users        |        |      devices       |        |    location_events    |
+--------------------+        +--------------------+        +-----------------------+
| id (PK)            | 1    * | id (PK)            | 1    * | id (PK)               |
| email (UQ)         +--------+ user_id (FK)       +--------+ device_id (FK)        |
| hashed_password    |        | device_identifier  |        | latitude, longitude   |
| name, role         |        | name, is_active    |        | accuracy_meters       |
| created_at         |        | last_latitude      |        | timestamp, created_at |
+--------------------+        | last_longitude     |        +-----------+-----------+
                              +---------+----------+                    |
                                        |                               |
                                        | 1                             | 1
                                        |                               |
                                        | *                           * |
+--------------------+        +---------+----------+                    |
|     geofences      |        |   geofence_events  |                    |
+--------------------+        +--------------------+                    |
| id (PK)            | 1    * | id (PK)            |                    |
| name, description  +--------+ geofence_id (FK)   |                    |
| type (CIRCLE/POLY) |        | device_id (FK)     +--------------------+
| center_lat, center_lon      | location_id (FK)   |
| radius_meters      |        | event_type         | (ENTER, EXIT, INSIDE, OUTSIDE)
| is_active          |        | previous_state     |
+---------+----------+        | current_state      |
          |                   | timestamp          |
          | 1                 +--------------------+
          |
          | *
+---------+----------+        +--------------------+
|  geofence_points   |        |     audit_logs     |
+--------------------+        +--------------------+
| id (PK)            |        | id (PK)            |
| geofence_id (FK)   |        | user_id (FK)       |
| latitude           |        | action, entity     |
| longitude          |        | entity_id          |
| sequence_order     |        | old_value (JSON)   |
+--------------------+        | new_value (JSON)   |
                              | timestamp          |
                              +--------------------+
```

---

## API Specification & cURL Examples

All endpoints (except `/api/v1/auth/login` and `/api/v1/auth/register`) require standard Bearer token authorization: `Authorization: Bearer <TOKEN>`.

### 1. Authenticate (Login)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=Admin@123"
```

### 2. Ingest GPS Coordinate & Evaluate Geofences
```bash
curl -X POST "http://localhost:8000/api/v1/locations" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "device_id": 1,
       "latitude": 11.0168,
       "longitude": 76.9558,
       "accuracy_meters": 5.0,
       "timestamp": "2026-10-01T12:00:00Z"
     }'
```
**Response Sample**:
```json
{
  "location_id": 4,
  "device_id": 1,
  "latitude": 11.0168,
  "longitude": 76.9558,
  "accuracy_meters": 5.0,
  "events": [
    {
      "id": 5,
      "geofence_id": 1,
      "geofence_name": "Headquarters Security Zone",
      "device_id": 1,
      "device_name": "Patrol Unit Alpha",
      "event_type": "ENTER",
      "previous_state": "OUTSIDE",
      "current_state": "INSIDE",
      "timestamp": "2026-10-01T12:00:00Z"
    }
  ]
}
```

### 3. Create Circular Geofence
```bash
curl -X POST "http://localhost:8000/api/v1/geofences" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Downtown Delivery Hub",
       "description": "500m logistics zone",
       "type": "CIRCLE",
       "center_latitude": 11.0168,
       "center_longitude": 76.9558,
       "radius_meters": 500.0,
       "is_active": true
     }'
```

### 4. Create Polygon Geofence
```bash
curl -X POST "http://localhost:8000/api/v1/geofences" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Airfield Restricted Area",
       "description": "Polygon airfield boundary",
       "type": "POLYGON",
       "is_active": true,
       "points": [
         {"latitude": 11.0150, "longitude": 76.9540, "sequence_order": 0},
         {"latitude": 11.0180, "longitude": 76.9540, "sequence_order": 1},
         {"latitude": 11.0180, "longitude": 76.9580, "sequence_order": 2},
         {"latitude": 11.0150, "longitude": 76.9580, "sequence_order": 3}
       ]
     }'
```

---

## Frontend UI & Real-Time Visualization

The frontend is a modern single-page dashboard built with Material UI v9 and Leaflet:
- **Interactive OpenStreetMap**: Render circular zones with custom radii, polygon polygons with colored outlines, and color-coded device markers.
- **Geofence Creator**: Switch between circular (picker + radius slider) and polygonal (click-to-plot vertices) modes with instant perimeter previews.
- **Live Operation Map**: Real-time multi-device tracking with layer toggle controls.
- **GPS Ingestion Simulator**: Test real-time coordinate injection, preset scenario triggers (Inside Circle, Inside Polygon, Jitter, Out of Bounds), and inspect instantaneous engine transition events.
- **Audit Logs & Analytics**: Recharts-powered event timeline and paginated administrative audit trail.

---

## Installation & Setup

### Option A: Docker Compose (Recommended)

1. Clone or extract repository into workspace.
2. Build and launch all containers:
   ```bash
   docker compose up --build -d
   ```
3. The services will automatically spin up:
   - **Frontend App**: `http://localhost:3000`
   - **FastAPI API & Swagger**: `http://localhost:8000/docs`
   - **MySQL Database**: `localhost:3307` (user: `geofence_user`, password: `geofence_password`)

### Option B: Local Manual Setup

#### 1. Database Setup
Create database in MySQL 8:
```sql
CREATE DATABASE geofencing_db;
CREATE USER 'geofence_user'@'localhost' IDENTIFIED BY 'geofence_password';
GRANT ALL PRIVILEGES ON geofencing_db.* TO 'geofence_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Run migrations & seed demo data
alembic upgrade head
python seed.py

# Launch server
uvicorn app.main:app --reload --port 8000
```
Swagger UI will be available at: `http://localhost:8000/docs`.

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open Vite dev server at: `http://localhost:5173`.

---

## Seed Data & Demo Credentials

When `seed.py` executes, it provisions the following users, devices, and geofences:

### User Credentials
| Role | Email | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin@example.com` | `Admin@123` |
| **Field Agent** | `user1@example.com` | `User@123` |

### Provisioned Geofences
1. **Headquarters Security Zone**: Circular boundary ($R = 300\text{m}$) centered at `(11.0168, 76.9558)`.
2. **Central Warehouse Depot**: 4-point polygon enclosing logistics grounds.
3. **Vehicle Fleet Parking**: Circular boundary ($R = 150\text{m}$) centered at `(11.0190, 76.9575)`.

### Provisioned Devices
- `DEVICE-001` (Assigned to Field Agent)
- `DEVICE-002` (Assigned to Administrator)
- `DEVICE-003` (Unassigned)

---

## Automated Testing Suite

The backend includes a comprehensive pytest suite with 42 tests covering coordinate formulas, spatial geometry, accuracy degraded edge cases, hysteresis boundaries, duplicate filtering, state machine transitions, and full REST API routes.

To execute tests:
```bash
cd backend
pytest -v
```

### Pytest Verification Summary
```
tests/test_coordinates.py::test_haversine_same_point PASSED
tests/test_coordinates.py::test_haversine_known_equator_distance PASSED
tests/test_coordinates.py::test_point_to_segment_distance PASSED
tests/test_circle.py::test_point_strictly_inside_circle PASSED
tests/test_circle.py::test_point_strictly_outside_circle PASSED
tests/test_circle.py::test_circle_hysteresis_when_already_inside PASSED
tests/test_polygon.py::test_point_strictly_inside_polygon PASSED
tests/test_polygon.py::test_point_strictly_outside_polygon PASSED
tests/test_polygon.py::test_polygon_hysteresis_outside PASSED
tests/test_state_machine.py::test_initial_fix_inside_generates_enter PASSED
tests/test_state_machine.py::test_outside_to_inside_generates_enter PASSED
tests/test_state_machine.py::test_inside_to_outside_generates_exit PASSED
tests/test_engine.py::test_engine_evaluates_multiple_geofences PASSED
tests/test_api_auth.py::test_login_success PASSED
tests/test_api_devices.py::test_create_and_list_device PASSED
tests/test_api_geofences.py::test_create_circular_geofence PASSED
tests/test_api_locations_and_events.py::test_ingest_location_generates_enter_event PASSED
...
============================= 42 passed in 5.81s =============================
```

---

## Postman Collection

Import the included Postman collection for complete end-to-end API testing:
- **File**: `postman/geofencing-api.postman_collection.json`
- **Pre-configured variables**:
  - `base_url`: `http://localhost:8000/api/v1`
  - Automatic `access_token` capture script upon executing `Login (Admin)`.
