# SwiftLogistics – Implementation Checklist

This document provides a clear roadmap for implementing the SwiftLogistics middleware system, including external legacy systems, business logic microservices, middleware, and supporting infrastructure.

---

## 1️⃣ External Systems (Legacy / Mock Services)

These simulate the systems you need to integrate.

| System | Technology | Purpose | Implementation Notes |
|--------|-----------|---------|--------------------|
| **CMS (Client Management System)** | Python / FastAPI | SOAP/XML interface | - Mock service simulating order creation.<br>- Accepts SOAP requests, responds with `createOrderResponse`.<br>- Maps payload for MI consumption. |
| **ROS (Route Optimization System)** | Go | REST/JSON high-performance API | - Receives addresses, returns optimized routes.<br>- High concurrency simulation.<br>- Provides response for MI orchestration. |
| **WMS (Warehouse Management System)** | Rust | TCP/IP messaging | - TCP server that receives dispatch instructions.<br>- Returns simple acknowledgment (`WMS_OK`).<br>- Simulates proprietary warehouse system. |

---

## 2️⃣ Microservices (Business Logic Layer)

These handle core business rules and workflows, exposed via REST APIs.

| Service | Technology | Responsibilities | API Examples |
|---------|-----------|-----------------|--------------|
| **Shipment Service** | FastAPI / Python | - Validate and create shipments<br>- Assign drivers<br>- Check warehouse availability<br>- Communicate with MI for orchestration | `POST /shipments`, `GET /shipments/{id}` |
| **Billing Service** | FastAPI / Python | - Calculate shipping costs<br>- Apply discounts & commissions<br>- Generate invoices | `POST /billing`, `GET /billing/{id}` |
| **Inventory Service** | FastAPI / Python | - Manage warehouse stock<br>- Reserve inventory for orders<br>- Update stock after dispatch | `GET /inventory`, `POST /inventory/reserve` |
| **Notification Service (Optional)** | FastAPI / Python | - Send email/SMS to clients/drivers<br>- Subscribe to Kafka events | `POST /notifications` |

**Key points for microservices:**
- Each service owns its **domain logic**.
- Should be **stateless** and **scalable**.
- Connect to **Kafka for async messaging** when needed.
- Expose **REST APIs for MI and API Manager**.

---

## 3️⃣ Middleware / Integration Layer

| Component | Technology | Role |
|-----------|-----------|------|
| **WSO2 Micro Integrator (MI)** | WSO2 MI | - Mediate between legacy systems & microservices<br>- Transform payloads (SOAP → JSON, JSON → TCP, etc.)<br>- Orchestrate multi-step workflows<br>- Handle retries, error handling, dead-letter queues |
| **WSO2 API Manager** | WSO2 APIM | - Expose all microservices and MI sequences as APIs<br>- Apply security (OAuth2/JWT)<br>- Throttling, caching, analytics<br>- Gateway for mobile apps and client portal |

---

## 4️⃣ Supporting Infrastructure

| Component | Technology | Notes |
|-----------|-----------|------|
| **Event Bus / Messaging** | Apache Kafka | - Async communication between services<br>- Topics for `orders`, `shipments`, `notifications`, `dead-letter-queue` |
| **Containerization** | Docker | - Each service runs in its own container<br>- Ensures consistency across environments |
| **Orchestration / Deployment** | Kubernetes | - Manage replicas, scaling, load balancing<br>- Ingress controller for external access<br>- Persistent Volumes for data/logs |
| **CI/CD** | GitHub Actions / Jenkins / Choreo | - Automate build, test, and deploy pipelines |

---

## 5️⃣ Implementation Order (Recommended)

1. **Setup Infrastructure**
   - Docker, Kubernetes, Kafka, WSO2 MI & APIM.  

2. **Implement External Legacy Services**
   - CMS (Python/FastAPI)  
   - ROS (Go)  
   - WMS (Rust)  

3. **Implement Microservices**
   - Shipment Service → connect to MI  
   - Billing Service → connect to MI  
   - Inventory Service → connect to MI  
   - Optional Notification Service → subscribe to Kafka events  

4. **Integrate with WSO2 MI**
   - Create proxy services, sequences, payload transformations.  
   - Connect MI to legacy systems and microservices.  

5. **Expose APIs via WSO2 API Manager**
   - Secure, throttle, and monitor APIs.  

6. **Set up Event-driven Flows**
   - Kafka topics, consumers, DLQ, and retries.  

7. **CI/CD and Kubernetes Deployment**
   - Automate builds, rolling updates, HPA, and monitoring.




# SwiftLogistics – Microservices Database & Tech Stack Guide

Each microservice in SwiftLogistics should have its own database for **encapsulation, scalability, resilience, and tech versatility**. This document details suggested tech stacks for each service and how they connect.

---

## 1️⃣ Shipment Service
- **Tech Stack:** Python + FastAPI + PostgreSQL
- **Why:**  
  - FastAPI → high-performance async APIs  
  - PostgreSQL → relational DB, ACID compliance for shipments
- **Connections:**  
  - **WSO2 MI:** REST API calls for order creation/status updates  
  - **Kafka:** publishes `shipment_created` events  

---

## 2️⃣ Billing Service
- **Tech Stack:** Python + FastAPI + MongoDB
- **Why:**  
  - Flexible document storage for invoices, discounts  
  - Learn both relational and NoSQL databases
- **Connections:**  
  - **WSO2 MI:** calls Billing Service to generate invoices when shipment confirmed  
  - **Kafka:** consumes `shipment_created` events, publishes `invoice_generated`  

---

## 3️⃣ Inventory Service
- **Tech Stack:** Node.js + NestJS + Redis (cache) + PostgreSQL (persistent)
- **Why:**  
  - NestJS → modern TypeScript framework, enterprise-ready  
  - Redis → fast stock/reservation checks  
  - PostgreSQL → persistent stock records
- **Connections:**  
  - **WSO2 MI:** queries stock before shipment confirmation  
  - **Kafka:** consumes `shipment_created`, publishes `inventory_updated`  

---

## 4️⃣ Notification Service (Optional)
- **Tech Stack:** Go + gRPC + RabbitMQ/Kafka
- **Why:**  
  - Go → lightweight, efficient, high-throughput  
  - gRPC → low-latency internal service communication  
  - Messaging system → reliable event-driven notifications
- **Connections:**  
  - **Kafka:** consumes `shipment_created` and `invoice_generated` events  
  - **WSO2 MI:** optional trigger for SOAP/REST notifications  

---

## 🔗 Connections Overview
1. **REST APIs:** Exposed by each microservice for MI orchestration.  
2. **Event-driven Messaging (Kafka):**  
   - `orders` → created by CMS → consumed by Shipment Service  
   - `shipment_created` → produced by Shipment → consumed by Billing & Inventory  
   - `invoice_generated` → produced by Billing → consumed by Notification Service  
3. **Payload Transformation:** WSO2 MI converts SOAP/XML → JSON/REST → TCP if needed.  
4. **Database Isolation:** Each microservice owns its DB; no direct DB queries between services.

---



![Alt text](https://drive.google.com/uc?export=view&id=1dRSy_ly47nd96S7Y26uyS4QlnGeBBWaO)

![Alt text](https://drive.google.com/uc?export=view&id=16RmAbmbDUE7Y60UJGIUsaplby_lb-iuy)

![Alt text](https://drive.google.com/uc?export=view&id=13eK7iRdkZhPUKtI2mnHI1tDGlXgqNIoH)

![Alt text](https://drive.google.com/uc?export=view&id=1vD9CzOBjRaPILoY5Gi23C5IKvYZTmSCi)

![Alt text](https://drive.google.com/uc?export=view&id=12uEFX9g67x34LCOajnztG5TBw9xvRHWY)

![Alt text](https://drive.google.com/uc?export=view&id=1Kp5XoN6OXOC6h_ilUHI7QSD0XofacOgK)

![Alt text](https://drive.google.com/uc?export=view&id=1pvD5g47hEtAMlPQUWrXyXSOvp0Nk6dVm)

![Alt text](https://drive.google.com/uc?export=view&id=17H_TF5pk7sisilmkUeu_WsNQ8vtqmWsR)

