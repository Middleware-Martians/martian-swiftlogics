# WMS API Testing Guide for Insomnia/Postman

This guide provides comprehensive API testing examples for the WMS (Warehouse Management System) service.

## Base URL
```
http://localhost:8002
```

## Test Collection

### 1. Health Check
**Method:** GET  
**URL:** `http://localhost:8002/health`  
**Description:** Check service health status  

**Expected Response:**
```json
{
    "status": "healthy",
    "service": "WMS",
    "timestamp": "2025-09-17T19:53:55.020874",
    "database": "wms_db"
}
```

---

### 2. Create Order
**Method:** POST  
**URL:** `http://localhost:8002/orders`  
**Headers:** `Content-Type: application/json`  
**Body:**
```json
{
    "order_number": "WMS001",
    "customer_id": 1001,
    "product_name": "Laptop Computer",
    "quantity": 2
}
```

**Expected Response:**
```json
{
    "id": 1,
    "order_number": "WMS001",
    "customer_id": 1001,
    "product_name": "Laptop Computer",
    "quantity": 2,
    "driver_id": null,
    "status": "received",
    "created_at": "2025-09-17T19:54:19.085359Z",
    "updated_at": "2025-09-17T19:54:19.085359Z"
}
```

---

### 3. Get All Orders
**Method:** GET  
**URL:** `http://localhost:8002/orders`  
**Query Parameters (Optional):**
- `skip=0` (pagination offset)
- `limit=100` (pagination limit)

**Expected Response:**
```json
[
    {
        "id": 1,
        "order_number": "WMS001",
        "customer_id": 1001,
        "product_name": "Laptop Computer",
        "quantity": 2,
        "driver_id": null,
        "status": "received",
        "created_at": "2025-09-17T19:54:19.085359Z",
        "updated_at": "2025-09-17T19:54:19.085359Z"
    }
]
```

---

### 4. Get Order by ID
**Method:** GET  
**URL:** `http://localhost:8002/orders/1`  

**Expected Response:**
```json
{
    "id": 1,
    "order_number": "WMS001",
    "customer_id": 1001,
    "product_name": "Laptop Computer",
    "quantity": 2,
    "driver_id": null,
    "status": "received",
    "created_at": "2025-09-17T19:54:19.085359Z",
    "updated_at": "2025-09-17T19:54:19.085359Z"
}
```

---

### 5. Update Order Status to In Warehouse
**Method:** PUT  
**URL:** `http://localhost:8002/warehouse/orders/1/status`  
**Headers:** `Content-Type: application/json`  
**Body:**
```json
{
    "status": "in_warehouse"
}
```

**Expected Response:**
```json
{
    "id": 1,
    "order_number": "WMS001",
    "customer_id": 1001,
    "product_name": "Laptop Computer",
    "quantity": 2,
    "driver_id": null,
    "status": "in_warehouse",
    "created_at": "2025-09-17T19:54:19.085359Z",
    "updated_at": "2025-09-17T19:55:07.123456Z"
}
```

---

### 6. Assign Driver to Order
**Method:** PUT  
**URL:** `http://localhost:8002/warehouse/orders/1/assign-driver`  
**Headers:** `Content-Type: application/json`  
**Body:**
```json
{
    "driver_id": 2001
}
```

**Expected Response:**
```json
{
    "id": 1,
    "order_number": "WMS001",
    "customer_id": 1001,
    "product_name": "Laptop Computer",
    "quantity": 2,
    "driver_id": 2001,
    "status": "loaded",
    "created_at": "2025-09-17T19:54:19.085359Z",
    "updated_at": "2025-09-17T19:55:19.185432Z"
}
```
*Note: Status automatically changes to "loaded" when driver is assigned*

---

### 7. Warehouse Dashboard
**Method:** GET  
**URL:** `http://localhost:8002/warehouse/dashboard`  

**Expected Response:**
```json
{
    "total_orders": 1,
    "status_breakdown": {
        "received": 0,
        "in_warehouse": 0,
        "loaded": 1,
        "delivered": 0
    },
    "driver_assignment": {
        "assigned": 1,
        "unassigned": 0
    },
    "timestamp": "2025-09-17T19:55:37.658572"
}
```

---

### 8. Get Orders by Status
**Method:** GET  
**URL:** `http://localhost:8002/orders/by-status/loaded`  

**Expected Response:**
```json
[
    {
        "id": 1,
        "order_number": "WMS001",
        "customer_id": 1001,
        "product_name": "Laptop Computer",
        "quantity": 2,
        "driver_id": 2001,
        "status": "loaded",
        "created_at": "2025-09-17T19:54:19.085359Z",
        "updated_at": "2025-09-17T19:55:19.185432Z"
    }
]
```

---

### 9. Get Orders by Driver
**Method:** GET  
**URL:** `http://localhost:8002/orders/by-driver/2001`  

**Expected Response:**
```json
[
    {
        "id": 1,
        "order_number": "WMS001",
        "customer_id": 1001,
        "product_name": "Laptop Computer",
        "quantity": 2,
        "driver_id": 2001,
        "status": "loaded",
        "created_at": "2025-09-17T19:54:19.085359Z",
        "updated_at": "2025-09-17T19:55:19.185432Z"
    }
]
```

---

### 10. Get Customer Orders
**Method:** GET  
**URL:** `http://localhost:8002/orders/customer/1001`  

**Expected Response:**
```json
[
    {
        "id": 1,
        "order_number": "WMS001",
        "customer_id": 1001,
        "product_name": "Laptop Computer",
        "quantity": 2,
        "driver_id": 2001,
        "status": "loaded",
        "created_at": "2025-09-17T19:54:19.085359Z",
        "updated_at": "2025-09-17T19:55:19.185432Z"
    }
]
```

---

### 11. Receive New Order into Warehouse
**Method:** POST  
**URL:** `http://localhost:8002/warehouse/receive-order`  
**Headers:** `Content-Type: application/json`  
**Body:**
```json
{
    "order_number": "WMS002",
    "customer_id": 1002,
    "product_name": "Desktop Computer",
    "quantity": 1
}
```

**Expected Response:**
```json
{
    "id": 2,
    "order_number": "WMS002",
    "customer_id": 1002,
    "product_name": "Desktop Computer",
    "quantity": 1,
    "driver_id": null,
    "status": "received",
    "created_at": "2025-09-17T20:00:00.000000Z",
    "updated_at": "2025-09-17T20:00:00.000000Z"
}
```

---

### 12. Update Order Details
**Method:** PUT  
**URL:** `http://localhost:8002/orders/1`  
**Headers:** `Content-Type: application/json`  
**Body:**
```json
{
    "product_name": "Gaming Laptop",
    "quantity": 3
}
```

**Expected Response:**
```json
{
    "id": 1,
    "order_number": "WMS001",
    "customer_id": 1001,
    "product_name": "Gaming Laptop",
    "quantity": 3,
    "driver_id": 2001,
    "status": "loaded",
    "created_at": "2025-09-17T19:54:19.085359Z",
    "updated_at": "2025-09-17T20:01:00.000000Z"
}
```

---

### 13. Mark Order as Delivered
**Method:** PUT  
**URL:** `http://localhost:8002/warehouse/orders/1/status`  
**Headers:** `Content-Type: application/json`  
**Body:**
```json
{
    "status": "delivered"
}
```

**Expected Response:**
```json
{
    "id": 1,
    "order_number": "WMS001",
    "customer_id": 1001,
    "product_name": "Gaming Laptop",
    "quantity": 3,
    "driver_id": 2001,
    "status": "delivered",
    "created_at": "2025-09-17T19:54:19.085359Z",
    "updated_at": "2025-09-17T20:02:00.000000Z"
}
```

---

### 14. Workflow Status Overview
**Method:** GET  
**URL:** `http://localhost:8002/warehouse/workflow-status`  

**Expected Response:**
```json
{
    "workflow_summary": {
        "total_orders": 2,
        "status_distribution": {
            "received": 1,
            "in_warehouse": 0,
            "loaded": 0,
            "delivered": 1
        },
        "driver_assignments": {
            "total_assigned": 1,
            "total_unassigned": 1,
            "assignment_rate": 50.0
        }
    },
    "recent_activity": [
        {
            "order_id": 1,
            "action": "status_updated",
            "from_status": "loaded",
            "to_status": "delivered",
            "timestamp": "2025-09-17T20:02:00.000000Z"
        }
    ],
    "timestamp": "2025-09-17T20:02:30.000000Z"
}
```

---

### 15. Delete Order
**Method:** DELETE  
**URL:** `http://localhost:8002/orders/2`  

**Expected Response:**
```json
{
    "message": "Order deleted successfully"
}
```

---

## Testing Workflow Scenarios

### Scenario 1: Complete Order Lifecycle
1. Create Order (POST `/orders`)
2. Move to Warehouse (PUT `/warehouse/orders/{id}/status` with "in_warehouse")
3. Assign Driver (PUT `/warehouse/orders/{id}/assign-driver`)
4. Mark Delivered (PUT `/warehouse/orders/{id}/status` with "delivered")
5. Check Dashboard (GET `/warehouse/dashboard`)

### Scenario 2: Error Testing
1. Try invalid status transition (e.g., "received" to "delivered")
2. Try to assign driver to delivered order
3. Try to create order with duplicate order_number
4. Try to get non-existent order

### Scenario 3: Filtering and Search
1. Create multiple orders with different statuses
2. Filter by status (GET `/orders/by-status/{status}`)
3. Filter by customer (GET `/orders/customer/{customer_id}`)
4. Filter by driver (GET `/orders/by-driver/{driver_id}`)

## Status Codes Reference

- **200 OK**: Successful operation
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data or business rule violation
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

## PowerShell Testing Examples

For Windows PowerShell users, here are some quick test commands:

```powershell
# Create Order
$body = @{order_number="WMS001";customer_id=1001;product_name="Laptop";quantity=2} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8002/orders -Method POST -Body $body -ContentType "application/json"

# Get Health
Invoke-WebRequest -Uri http://localhost:8002/health -Method GET

# Update Status
$body = @{status="in_warehouse"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8002/warehouse/orders/1/status -Method PUT -Body $body -ContentType "application/json"

# Assign Driver
$body = @{driver_id=2001} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8002/warehouse/orders/1/assign-driver -Method PUT -Body $body -ContentType "application/json"

# Dashboard
Invoke-WebRequest -Uri http://localhost:8002/warehouse/dashboard -Method GET
```