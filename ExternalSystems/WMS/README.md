# WMS (Warehouse Management System) Service

A FastAPI-based microservice for managing warehouse operations, order workflow, and driver assignments within the SwiftLogistics platform.

## Features

- **Order Management**: Complete CRUD operations for warehouse orders
- **Workflow Management**: Status transitions (received → in_warehouse → loaded → delivered)
- **Driver Assignment**: Automatic status updates when drivers are assigned
- **Analytics Dashboard**: Real-time warehouse metrics and status breakdown
- **Validation**: Business rule enforcement for status transitions
- **Health Monitoring**: Service health checks and database connectivity

## Architecture

- **Framework**: FastAPI 0.104.1 with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Port**: 8002
- **Database**: wms_db

## Database Schema

### Order Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    product_name VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    driver_id INTEGER NULL,
    status VARCHAR DEFAULT 'received' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Health Check
- **GET** `/health` - Service health status

### Order Management
- **POST** `/orders` - Create new order
- **GET** `/orders` - List all orders with pagination
- **GET** `/orders/{id}` - Get specific order
- **PUT** `/orders/{id}` - Update order details
- **DELETE** `/orders/{id}` - Delete order

### Warehouse Operations
- **POST** `/warehouse/receive-order` - Receive new order into warehouse
- **PUT** `/warehouse/orders/{id}/assign-driver` - Assign driver to order
- **PUT** `/warehouse/orders/{id}/status` - Update order status with validation

### Analytics & Monitoring
- **GET** `/warehouse/dashboard` - Warehouse analytics dashboard
- **GET** `/warehouse/workflow-status` - Current workflow status overview

### Filtering & Search
- **GET** `/orders/by-status/{status}` - Filter orders by status
- **GET** `/orders/by-driver/{driver_id}` - Filter orders by driver
- **GET** `/orders/customer/{customer_id}` - Get customer orders

## Status Workflow

The WMS enforces a strict workflow for order status transitions:

```
received → in_warehouse → loaded → delivered
```

### Valid Transitions
- `received` → `in_warehouse`
- `in_warehouse` → `loaded` or back to `received`
- `loaded` → `delivered`

### Automatic Status Updates
- When a driver is assigned to an order in `received` or `in_warehouse` status, it automatically moves to `loaded`

## Request/Response Models

### Create Order
```json
{
    "order_number": "WMS001",
    "customer_id": 1001,
    "product_name": "Laptop Computer",
    "quantity": 2
}
```

### Order Response
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

### Status Update
```json
{
    "status": "in_warehouse"
}
```

### Driver Assignment
```json
{
    "driver_id": 2001
}
```

### Dashboard Response
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

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- PostgreSQL database (handled by docker-compose)

### Running the Service

1. **Start all services**:
```bash
docker-compose up -d
```

2. **Check service health**:
```bash
curl http://localhost:8002/health
```

3. **View logs**:
```bash
docker-compose logs wms
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (set via docker-compose)

## Testing Examples

### 1. Create a New Order
```bash
# PowerShell
$body = @{
    order_number = "WMS001"
    customer_id = 1001
    product_name = "Laptop Computer"
    quantity = 2
} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8002/orders -Method POST -Body $body -ContentType "application/json"

# curl
curl -X POST http://localhost:8002/orders \
  -H "Content-Type: application/json" \
  -d '{"order_number":"WMS001","customer_id":1001,"product_name":"Laptop Computer","quantity":2}'
```

### 2. Move Order to Warehouse
```bash
# PowerShell
$body = @{ status = "in_warehouse" } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8002/warehouse/orders/1/status -Method PUT -Body $body -ContentType "application/json"

# curl
curl -X PUT http://localhost:8002/warehouse/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"in_warehouse"}'
```

### 3. Assign Driver
```bash
# PowerShell
$body = @{ driver_id = 2001 } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8002/warehouse/orders/1/assign-driver -Method PUT -Body $body -ContentType "application/json"

# curl
curl -X PUT http://localhost:8002/warehouse/orders/1/assign-driver \
  -H "Content-Type: application/json" \
  -d '{"driver_id":2001}'
```

### 4. Check Dashboard
```bash
# PowerShell
Invoke-WebRequest -Uri http://localhost:8002/warehouse/dashboard -Method GET

# curl
curl http://localhost:8002/warehouse/dashboard
```

### 5. Get Orders by Status
```bash
# PowerShell
Invoke-WebRequest -Uri http://localhost:8002/orders/by-status/loaded -Method GET

# curl
curl http://localhost:8002/orders/by-status/loaded
```

## Error Handling

The service provides comprehensive error handling:

- **400 Bad Request**: Invalid data or business rule violations
- **404 Not Found**: Order not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Database or system errors

### Common Error Scenarios

1. **Invalid Status Transition**:
```json
{
    "detail": "Cannot transition from 'delivered' to 'received'. Valid next statuses: []"
}
```

2. **Order Not Found**:
```json
{
    "detail": "Order not found"
}
```

3. **Duplicate Order Number**:
```json
{
    "detail": "Order with this order number already exists"
}
```

## Business Rules

1. **Status Transitions**: Enforced workflow prevents invalid status changes
2. **Driver Assignment**: Can only assign drivers to orders in `received` or `in_warehouse` status
3. **Auto-Status Update**: Assigning a driver automatically moves order to `loaded` status
4. **Unique Order Numbers**: Each order must have a unique order_number
5. **Required Fields**: order_number, customer_id, product_name, and quantity are mandatory

## Integration with Other Services

The WMS service is designed to integrate with:

- **CMS (Client Management System)**: Customer information and order validation
- **ROS (Route Optimization System)**: Driver assignments and route planning
- **External Systems**: Inventory management and shipping providers

## Performance Considerations

- Database indexing on order_number, customer_id, and status fields
- Pagination for large result sets
- Connection pooling for database operations
- Async operations for better throughput

## Monitoring and Observability

- Health check endpoint for service monitoring
- Structured logging for debugging
- Database connection retry logic
- Request/response logging for audit trails

## Future Enhancements

- Inventory integration
- Real-time notifications
- Advanced analytics and reporting
- Bulk operations support
- Role-based access control
- API rate limiting