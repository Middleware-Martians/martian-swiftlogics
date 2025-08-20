# WMS (Warehouse Management System) – Mock Service

**Purpose:** Simulate warehouse dispatch instructions and acknowledgment over TCP/IP.

**Technology Stack:**
- Language: Rust
- Framework: Tokio (async TCP server)
- Database: PostgreSQL or SQLite (optional for inventory and dispatches)

---

## Database Schema (Optional)
```sql
CREATE TABLE inventory (
    item_id SERIAL PRIMARY KEY,
    item_name VARCHAR(100),
    quantity INT,
    warehouse_location VARCHAR(100)
);

CREATE TABLE dispatches (
    dispatch_id SERIAL PRIMARY KEY,
    order_id INT,
    item_id INT,
    quantity INT,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## TCP Server Behavior
- Listen on port (e.g., 5000)
- Accept messages in JSON or plain text format
- Return acknowledgment (`WMS_OK`)

### Sample Message to WMS
```json
{
  "orderId": 1001,
  "items": [
    {"itemId": 1, "quantity": 2},
    {"itemId": 2, "quantity": 1}
  ]
}
```

### Acknowledgment Response
```json
{
  "status": "WMS_OK",
  "message": "Dispatch received"
}
```

---

**Better to Have:**
- Endpoint to query stock (`GET /inventory/:itemId`)
- Simulate delayed acknowledgment for testing retries in MI
- Logging of received dispatch messages for integration testing

