# WMS (Warehouse Management System) FastAPI Implementation Guide

## Overview
The WMS is a FastAPI-based microservice that manages warehouse operations, order workflows, and driver assignments. It provides comprehensive order lifecycle management from receipt to delivery.

## Architecture Components

### 1. Database Layer
- **PostgreSQL Database**: `wms_db` 
- **SQLAlchemy ORM**: Database abstraction and model management
- **Connection Pooling**: Efficient database connection management
- **Migration Support**: Database schema evolution

### 2. API Layer
- **FastAPI Framework**: High-performance async web framework
- **Pydantic Models**: Data validation and serialization
- **OpenAPI Integration**: Automatic API documentation
- **CORS Support**: Cross-origin resource sharing

### 3. Business Logic Layer
- **Workflow Management**: Status transition validation
- **Driver Assignment**: Automatic status updates
- **Analytics Engine**: Real-time dashboard metrics
- **Validation Rules**: Business rule enforcement

## Key Features

### Order Management
- Full CRUD operations for warehouse orders
- Unique order number validation
- Customer association and tracking
- Product and quantity management

### Workflow Engine
The WMS implements a strict workflow for order processing:

```
received → in_warehouse → loaded → delivered
```

**Transition Rules:**
- `received` can transition to `in_warehouse`
- `in_warehouse` can transition to `loaded` or back to `received`
- `loaded` can transition to `delivered`

**Automatic Triggers:**
- Assigning a driver automatically moves order to `loaded` status
- Status updates are timestamped for audit trail

### Driver Management
- Driver assignment to orders
- Automatic status progression on assignment
- Driver-based order filtering
- Assignment analytics

### Analytics & Reporting
- Real-time dashboard with order metrics
- Status breakdown and distribution
- Driver assignment rates
- Workflow status overview

## Implementation Details

### Database Schema
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

-- Indexes for performance
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_driver_id ON orders(driver_id);
CREATE INDEX idx_orders_order_number ON orders(order_number);
```

### Data Models

#### Core Models
```python
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    driver_id = Column(Integer, nullable=True, index=True)
    status = Column(String, default="received", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

#### Pydantic Models
```python
class OrderCreate(BaseModel):
    order_number: str
    customer_id: int
    product_name: str
    quantity: int
    status: Optional[str] = "received"

class OrderUpdate(BaseModel):
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str

class DriverAssignment(BaseModel):
    driver_id: int
```

### API Endpoints

#### Health & Monitoring
- `GET /health` - Service health check
- `GET /warehouse/dashboard` - Analytics dashboard
- `GET /warehouse/workflow-status` - Workflow overview

#### Order Management
- `POST /orders` - Create order
- `GET /orders` - List orders (with pagination)
- `GET /orders/{id}` - Get specific order
- `PUT /orders/{id}` - Update order
- `DELETE /orders/{id}` - Delete order

#### Warehouse Operations
- `POST /warehouse/receive-order` - Receive new order
- `PUT /warehouse/orders/{id}/assign-driver` - Assign driver
- `PUT /warehouse/orders/{id}/status` - Update status

#### Filtering & Search
- `GET /orders/by-status/{status}` - Filter by status
- `GET /orders/by-driver/{driver_id}` - Filter by driver
- `GET /orders/customer/{customer_id}` - Customer orders

### Business Logic Implementation

#### Status Validation
```python
def validate_status(status: str) -> bool:
    valid_statuses = ["received", "in_warehouse", "loaded", "delivered"]
    return status in valid_statuses

def validate_status_transition(current_status: str, new_status: str) -> bool:
    allowed_transitions = {
        "received": ["in_warehouse"],
        "in_warehouse": ["loaded", "received"],
        "loaded": ["delivered"],
        "delivered": []
    }
    return new_status in allowed_transitions.get(current_status, [])
```

#### Driver Assignment Logic
```python
def assign_driver(order_id: int, driver_id: int, db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if order.status not in ["received", "in_warehouse"]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot assign driver to this order status"
        )
    
    order.driver_id = driver_id
    order.status = "loaded"  # Auto-update status
    order.updated_at = datetime.utcnow()
    
    db.commit()
    return order
```

### Error Handling

The service implements comprehensive error handling:

```python
class OrderNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Order not found")

class InvalidStatusTransitionException(HTTPException):
    def __init__(self, current_status: str, new_status: str):
        super().__init__(
            status_code=400,
            detail=f"Cannot transition from '{current_status}' to '{new_status}'"
        )

class DuplicateOrderException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Order with this order number already exists"
        )
```

## Deployment Configuration

### Docker Setup
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Docker Compose Integration
```yaml
wms:
  build: ./WMS
  container_name: swiftlogistics_wms
  restart: always
  ports:
    - "8002:8002"
  depends_on:
    postgres:
      condition: service_healthy
  environment:
    - DATABASE_URL=postgresql://admin_user:admin_password@postgres:5432/wms_db
```

## Testing and Validation

The WMS service has been tested and validated with the following scenarios:

### Successful Test Cases
1. **Service Health Check**: ✅ Confirmed service running on port 8002
2. **Order Creation**: ✅ Successfully created order with auto-status "received"
3. **Status Transitions**: ✅ Updated order from "received" to "in_warehouse"
4. **Driver Assignment**: ✅ Assigned driver with auto-status change to "loaded"
5. **Dashboard Analytics**: ✅ Retrieved real-time warehouse metrics
6. **Workflow Validation**: ✅ Enforced business rules for status transitions

### Test Results Summary
```
✅ Health Check: Service healthy, database connected
✅ Order CRUD: Full create, read, update, delete operations
✅ Workflow Engine: Status transitions working correctly
✅ Driver Management: Assignment with auto-status updates
✅ Analytics Dashboard: Real-time metrics and breakdowns
✅ Data Validation: Proper error handling and validation
```

## Integration Points

### With CMS (Client Management System)
- Customer validation for order creation
- Customer order history retrieval
- Customer status notifications

### With ROS (Route Optimization System)
- Driver availability checking
- Route planning integration
- Delivery optimization

### External Systems
- Inventory management integration
- Shipping provider APIs
- Notification services

## Future Enhancements

### Planned Features
- Real-time notifications
- Advanced analytics and reporting
- Inventory integration
- Mobile API support

### Scalability Improvements
- Horizontal scaling support
- Microservice decomposition
- Event-driven architecture
- Caching layer implementation

### Integration Enhancements
- Third-party shipping APIs
- ERP system integration
- IoT device integration
- Machine learning for predictions