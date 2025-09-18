# ROS Service - Insomnia Test Collection

## Base URL: `http://localhost:8001`

---

## 🏥 Health Check

### Health Check
**Method**: `GET`
**URL**: `http://localhost:8001/health`

---

## 👨‍🚗 Driver Management

### 1. Create Driver
**Method**: `POST`
**URL**: `http://localhost:8001/drivers`
**Headers**: `Content-Type: application/json`
**Body**:
```json
{
    "name": "John Silva",
    "vehicle_number": "CAA-1234",
    "contact_number": "+94771234567",
    "current_location_lat": 6.9271,
    "current_location_long": 79.8612
}
```

### 2. Get All Drivers
**Method**: `GET`
**URL**: `http://localhost:8001/drivers`

### 3. Get All Drivers (Paginated)
**Method**: `GET`
**URL**: `http://localhost:8001/drivers?skip=0&limit=10`

### 4. Get Specific Driver
**Method**: `GET`
**URL**: `http://localhost:8001/drivers/1`

### 5. Update Driver
**Method**: `PUT`
**URL**: `http://localhost:8001/drivers/1`
**Headers**: `Content-Type: application/json`
**Body**:
```json
{
    "name": "John Silva Updated",
    "vehicle_number": "CAA-1234",
    "contact_number": "+94771234567",
    "current_location_lat": 6.9271,
    "current_location_long": 79.8612
}
```

### 6. Delete Driver
**Method**: `DELETE`
**URL**: `http://localhost:8001/drivers/1`

---

## 📦 Order Management

### 1. Create Order
**Method**: `POST`
**URL**: `http://localhost:8001/orders`
**Headers**: `Content-Type: application/json`
**Body**:
```json
{
    "customer_id": 201,
    "product_name": "Mars Rover Kit",
    "quantity": 1,
    "address": "Galle, Sri Lanka"
}
```

### 2. Get All Orders
**Method**: `GET`
**URL**: `http://localhost:8001/orders`

### 3. Get Orders by Status
**Method**: `GET`
**URL**: `http://localhost:8001/orders?status=pending`

### 4. Get Orders (Paginated)
**Method**: `GET`
**URL**: `http://localhost:8001/orders?skip=0&limit=10`

### 5. Get Specific Order
**Method**: `GET`
**URL**: `http://localhost:8001/orders/1`

### 6. Update Order
**Method**: `PUT`
**URL**: `http://localhost:8001/orders/1`
**Headers**: `Content-Type: application/json`
**Body**:
```json
{
    "customer_id": 201,
    "product_name": "Mars Rover Kit Deluxe",
    "quantity": 2,
    "address": "Galle, Sri Lanka",
    "driver_id": 1
}
```

### 7. Delete Order
**Method**: `DELETE`
**URL**: `http://localhost:8001/orders/1`

---

## 🗺️ Route Optimization

### Optimize Routes
**Method**: `POST`
**URL**: `http://localhost:8001/optimize-routes`
**Headers**: `Content-Type: application/json`
**Body**:
```json
{
    "order_ids": [1, 2, 3],
    "available_driver_ids": [1, 2]
}
```

---

## 🔧 Utility Endpoints

### 1. Get Driver Orders
**Method**: `GET`
**URL**: `http://localhost:8001/drivers/1/orders`

### 2. Update Order Status
**Method**: `PUT`
**URL**: `http://localhost:8001/orders/1/status?status=in_transit`

### 3. Get System Statistics
**Method**: `GET`
**URL**: `http://localhost:8001/statistics`

---

## 📊 Sample Test Data

### Driver Test Data

**Driver 1 (Colombo):**
```json
{
    "name": "John Silva",
    "vehicle_number": "CAA-1234",
    "contact_number": "+94771234567",
    "current_location_lat": 6.9271,
    "current_location_long": 79.8612
}
```

**Driver 2 (Kandy):**
```json
{
    "name": "Sarah Perera",
    "vehicle_number": "CBB-5678",
    "contact_number": "+94772345678",
    "current_location_lat": 7.2906,
    "current_location_long": 80.6337
}
```

**Driver 3 (Galle):**
```json
{
    "name": "Kamal Fernando",
    "vehicle_number": "CCC-9012",
    "contact_number": "+94773456789",
    "current_location_lat": 6.0535,
    "current_location_long": 80.2210
}
```

### Order Test Data

**Order 1 (Galle):**
```json
{
    "customer_id": 201,
    "product_name": "Mars Rover Kit",
    "quantity": 1,
    "address": "Galle, Sri Lanka"
}
```

**Order 2 (Jaffna):**
```json
{
    "customer_id": 202,
    "product_name": "Oxygen Generator",
    "quantity": 2,
    "address": "Jaffna, Sri Lanka"
}
```

**Order 3 (Anuradhapura):**
```json
{
    "customer_id": 203,
    "product_name": "Solar Panel Array",
    "quantity": 3,
    "address": "Anuradhapura, Sri Lanka"
}
```

**Order 4 (Batticaloa):**
```json
{
    "customer_id": 204,
    "product_name": "Communication Array",
    "quantity": 1,
    "address": "Batticaloa, Sri Lanka"
}
```

**Order 5 (Kurunegala):**
```json
{
    "customer_id": 205,
    "product_name": "Water Purifier",
    "quantity": 2,
    "address": "Kurunegala, Sri Lanka"
}
```

---

## 🧪 Complete Test Sequence

### 1. Initial Setup
1. **Health Check** - Verify service is running
2. **Create 3 Drivers** - Use the driver test data above
3. **Create 5 Orders** - Use the order test data above

### 2. Basic CRUD Testing
4. **Get All Drivers** - Verify all drivers are created
5. **Get All Orders** - Verify all orders are created
6. **Get Specific Driver** - Test individual driver retrieval
7. **Get Specific Order** - Test individual order retrieval

### 3. Route Optimization Testing
8. **Optimize Routes** - Assign 5 orders to 3 drivers
9. **Check Statistics** - Verify order assignments
10. **Get Driver Orders** - Check orders assigned to each driver

### 4. Status Management
11. **Update Order Status** - Change orders to "in_transit"
12. **Get Orders by Status** - Filter orders by status
13. **Check Statistics Again** - Verify status changes

### 5. Update Operations
14. **Update Driver Info** - Modify driver details
15. **Update Order** - Modify order details

### 6. Edge Case Testing
16. **Create Order with Invalid Driver** - Test error handling
17. **Delete Driver with Active Orders** - Test business rules
18. **Optimize with No Orders** - Test empty data handling

---

## 📈 Expected Status Codes

- **200 OK**: Successful GET, PUT operations
- **201 Created**: Successful POST operations
- **204 No Content**: Successful DELETE operations
- **400 Bad Request**: Invalid data or business rule violations
- **404 Not Found**: Resource not found
- **422 Validation Error**: Pydantic model validation errors

---

## 🔗 Related Services

- **CMS Service**: http://localhost:8000
- **PostgreSQL Database**: localhost:5432
- **API Documentation**: http://localhost:8001/docs