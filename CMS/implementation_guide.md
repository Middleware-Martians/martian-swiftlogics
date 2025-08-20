# CMS (Client Management System) – Mock Service

**Purpose:** Simulate order creation and management, accept SOAP requests, and return responses for WSO2 Micro Integrator.

**Technology Stack:**
- Language: Python
- Framework: FastAPI
- SOAP Handling: Spyne or Zeep
- Database: PostgreSQL or SQLite (optional)

---

## Database Schema (Optional)
```sql
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    client_name VARCHAR(100),
    client_email VARCHAR(100),
    pickup_address TEXT,
    delivery_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'PENDING'
);
```

---

## Endpoints

### 1. POST /soap/createOrder
- **Description:** Accepts SOAP XML to create a new order.
- **Request Example:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ord="http://cms.orders.com/">
   <soapenv:Header/>
   <soapenv:Body>
      <ord:createOrder>
         <ord:clientName>Nimna Pathum</ord:clientName>
         <ord:clientEmail>nimna@example.com</ord:clientEmail>
         <ord:pickupAddress>Colombo, SL</ord:pickupAddress>
         <ord:deliveryAddress>Kandy, SL</ord:deliveryAddress>
      </ord:createOrder>
   </soapenv:Body>
</soapenv:Envelope>
```
- **Response Example:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Body>
      <ord:createOrderResponse>
         <ord:orderId>1001</ord:orderId>
         <ord:status>CREATED</ord:status>
      </ord:createOrderResponse>
   </soapenv:Body>
</soapenv:Envelope>
```

### Optional Endpoints
- `GET /soap/orders` – List all orders
- `POST /soap/updateOrderStatus` – Update order status

---

**Better to Have:**
- Logging of received requests
- Deterministic responses for integration testing

