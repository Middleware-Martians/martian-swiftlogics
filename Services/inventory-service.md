# Inventory Service – Microservice Documentation

**Responsibilities:**
- Manage warehouse stock
- Reserve inventory for orders
- Update stock after dispatch

**Technology Stack & DB Preference:**
- Language: Node.js (TypeScript) + NestJS
- Database: PostgreSQL (persistent stock) + Redis (cache for stock availability)
- Messaging: Kafka to consume `shipment_created` events

---

## Database Schema
```sql
CREATE TABLE inventory (
    item_id SERIAL PRIMARY KEY,
    item_name VARCHAR(100),
    quantity INT,
    warehouse_location VARCHAR(100)
);

CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    shipment_id INT,
    item_id INT,
    quantity INT,
    status VARCHAR(50) DEFAULT 'RESERVED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Endpoints

### GET /inventory
- List all stock
- **Response Example:**
```json
[
  {"itemId":1,"itemName":"Box","quantity":100,"warehouseLocation":"Colombo"},
  {"itemId":2,"itemName":"Crate","quantity":50,"warehouseLocation":"Kandy"}
]
```

### POST /inventory/reserve
- Reserve stock for a shipment
- **Request Body:**
```json
{
  "shipmentId": 5001,
  "items": [{"itemId": 1, "quantity": 2}]
}
```
- **Response Example:**
```json
{
  "reservationId": 3001,
  "status": "RESERVED"
}
```

---

## Integration Notes
- MI queries stock before confirming shipment
- Consumes `shipment_created` events and updates inventory
- Publishes `inventory_updated` events
- Stateless service; scalable horizontally

