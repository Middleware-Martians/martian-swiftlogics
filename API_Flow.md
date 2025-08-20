# SwiftLogistics – API Flow and Integration

## 1️⃣ Client Portal / Mobile App → API Manager

- **API Manager** exposes all APIs to external clients.  
- Clients **never call microservices directly**; all requests go through API Manager.  
- Responsibilities of API Manager:  
  - **Authentication & Authorization:** OAuth2 / JWT  
  - **Rate limiting / Throttling**  
  - **Caching & Analytics**  

**Key Point:** API Manager does **not directly call Kafka**. It routes API requests to either the **API Gateway** or **Micro Integrator** depending on the integration type.

---

## 2️⃣ API Manager → API Gateway / Micro Integrator

In WSO2, the **API Gateway** is the runtime component of API Manager that forwards requests.

### a) Request for a Microservice

- Example: `/shipments/create` → REST API of **Shipment Service**  
- Flow:  
  1. Client calls API Manager endpoint.  
  2. API Manager routes request to **API Gateway**.  
  3. API Gateway **forwards REST request** directly to the microservice.  
  4. Microservice may **publish Kafka events** or call other internal services asynchronously.  

### b) Request for a Legacy System

- Example: `/createOrder` → CMS (SOAP/XML)  
- Flow:  
  1. Client calls API Manager endpoint.  
  2. API Manager routes request to **Micro Integrator (MI)**.  
  3. MI:  
     - Transforms request (e.g., JSON → SOAP/XML)  
     - Calls external system (CMS / ROS / WMS)  
     - Receives response  
     - Transforms response back (SOAP/XML → JSON)  
  4. MI returns response to API Manager → API Manager returns to client.

---

## 3️⃣ Kafka Events

- Kafka is used for **async messaging between microservices**, not for client API requests.  
- Examples:  
  - **Shipment Service** publishes `shipment_created` → consumed by Billing & Inventory.  
  - **Notification Service** consumes `shipment_created` or `invoice_generated`.  
- Clients **do not produce Kafka messages**; they interact only via REST APIs exposed through API Manager.

---

## ✅ Simplified Flow

