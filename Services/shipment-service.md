# Shipment Service – Microservice Documentation

**Responsibilities:**
- Validate and create shipments
- Assign drivers
- Check warehouse availability via WMS
- Publish `shipment_created` events to Kafka

**Technology Stack & DB Preference:**
- Language: Python
- Framework: FastAPI
- Database: PostgreSQL (relational, strong ACID compliance)
- Messaging: Kafka for async events

---

## Database Schema
```sql
CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    client_name VARCHAR(100),
    pickup_address TEXT,
    delivery_address TEXT,
    driver_id INT,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Endpoints

### POST /shipments
- Create a new shipment
- **Request Body:**
```json
{
  "orderId": 1001,
  "clientName": "Nimna Pathum",
  "pickupAddress": "Colombo, SL",
  "deliveryAddress": "Kandy, SL"
}
```
- **Response:**
```json
{
  "shipmentId": 5001,
  "status": "CREATED"
}
```

### GET /shipments/{id}
- Retrieve shipment details
- **Response:**
```json
{
  "shipmentId": 5001,
  "orderId": 1001,
  "clientName": "Nimna Pathum",
  "pickupAddress": "Colombo, SL",
  "deliveryAddress": "Kandy, SL",
  "driverId": 12,
  "status": "IN_TRANSIT",
  "createdAt": "2025-08-21T10:00:00Z"
}
```

---

## Integration Notes
- Micro Integrator calls this service via REST API
- Publishes Kafka event `shipment_created` for downstream services
- Stateless service; can scale horizontally

