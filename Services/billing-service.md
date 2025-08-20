# Billing Service – Microservice Documentation

**Responsibilities:**
- Calculate shipping costs
- Apply discounts and commissions
- Generate invoices
- Consume `shipment_created` events

**Technology Stack & DB Preference:**
- Language: Python
- Framework: FastAPI
- Database: MongoDB (flexible for invoice structures)
- Messaging: Kafka to consume `shipment_created` and produce `invoice_generated`

---

## Database Schema
```json
{
  "invoiceId": "ObjectId",
  "shipmentId": 5001,
  "orderId": 1001,
  "clientName": "Nimna Pathum",
  "amount": 150.0,
  "currency": "LKR",
  "status": "PAID",
  "createdAt": "2025-08-21T10:30:00Z"
}
```

---

## Endpoints

### POST /billing
- Generate an invoice
- **Request Body:**
```json
{
  "shipmentId": 5001,
  "orderId": 1001
}
```
- **Response:**
```json
{
  "invoiceId": "64f123456789abcdef123456",
  "status": "GENERATED"
}
```

### GET /billing/{id}
- Retrieve invoice details
- **Response:**
```json
{
  "invoiceId": "64f123456789abcdef123456",
  "shipmentId": 5001,
  "amount": 150.0,
  "status": "PAID"
}
```

---

## Integration Notes
- Subscribes to Kafka `shipment_created` events
- Publishes `invoice_generated` for Notification Service
- No direct DB access from other services

