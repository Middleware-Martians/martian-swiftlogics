# ROS (Route Optimization System) – Mock Service

**Purpose:** Accept a list of addresses and return an optimized route with total distance/time.

**Technology Stack:**
- Language: Go
- Framework: Gin or Fiber (REST API)
- Database: PostgreSQL or SQLite (optional for storing routes)

---

## Database Schema (Optional)
```sql
CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    origin TEXT,
    destination TEXT,
    distance_km FLOAT,
    estimated_time_min INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Endpoints

### 1. POST /routes/optimize
- **Description:** Accepts a list of addresses and returns optimized route.
- **Request Body Example:**
```json
{
  "addresses": [
    "Colombo, SL",
    "Kandy, SL",
    "Galle, SL"
  ]
}
```
- **Response Example:**
```json
{
  "optimizedRoute": ["Colombo, SL", "Galle, SL", "Kandy, SL"],
  "totalDistance": 250,
  "estimatedTime": 300
}
```

### 2. GET /routes/:id
- **Description:** Retrieve route details by route ID
- **Response Example:**
```json
{
  "routeId": 1,
  "origin": "Colombo, SL",
  "destination": "Kandy, SL",
  "distance": 120,
  "estimatedTime": 180
}
```

---

**Better to Have:**
- Mock concurrency simulation for high load
- Optional vehicle type or priority parameter to influence route optimization
- Logging requests for integration testing

