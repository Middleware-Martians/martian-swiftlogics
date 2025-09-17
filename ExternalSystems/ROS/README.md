# ROS (Route Optimization System) Service

## Overview

The ROS (Route Optimization System) is a microservice built with FastAPI and PostgreSQL that handles driver management, order assignment, and route optimization for the SwiftLogistics platform. This service is designed following microservice architecture principles with asynchronous processing capabilities.

## Architecture Features

- **Microservice Design**: Independent service with its own database (ros_db)
- **RESTful API**: Standard HTTP methods for all operations
- **Asynchronous Processing**: Non-blocking route optimization algorithms
- **Scalable Architecture**: Designed to handle multiple concurrent requests
- **Database Isolation**: Separate PostgreSQL database for data integrity
- **Container Support**: Fully containerized with Docker

## Database Schema

### Drivers Table
```sql
CREATE TABLE drivers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    vehicle_number VARCHAR UNIQUE NOT NULL,
    contact_number VARCHAR,
    current_location_lat FLOAT NOT NULL,
    current_location_long FLOAT NOT NULL
);
```

### Orders Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_name VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    address VARCHAR NOT NULL,
    driver_id INTEGER REFERENCES drivers(id),
    status VARCHAR DEFAULT 'pending'
);
```

## API Endpoints

### Health Check
- **GET** `/health` - Service health status

### Driver Management (CRUD)
- **POST** `/drivers` - Create new driver
- **GET** `/drivers` - List all drivers (with pagination)
- **GET** `/drivers/{driver_id}` - Get specific driver
- **PUT** `/drivers/{driver_id}` - Update driver information
- **DELETE** `/drivers/{driver_id}` - Delete driver

### Order Management (CRUD)
- **POST** `/orders` - Create new order
- **GET** `/orders` - List all orders (with status filter and pagination)
- **GET** `/orders/{order_id}` - Get specific order
- **PUT** `/orders/{order_id}` - Update order
- **DELETE** `/orders/{order_id}` - Delete order

### Route Optimization
- **POST** `/optimize-routes` - Optimize delivery routes

### Additional Endpoints
- **GET** `/drivers/{driver_id}/orders` - Get orders assigned to driver
- **PUT** `/orders/{order_id}/status` - Update order status
- **GET** `/statistics` - Get system statistics

## Service Configuration

### Port: 8001
### Database: ros_db (PostgreSQL)
### Dependencies:
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- psycopg2-binary 2.9.9
- uvicorn 0.24.0

## Testing Examples

### 1. Create Drivers

**Create Driver 1 (Colombo):**
```bash
POST http://localhost:8001/drivers
Content-Type: application/json

{
    "name": "John Silva",
    "vehicle_number": "CAA-1234",
    "contact_number": "+94771234567",
    "current_location_lat": 6.9271,
    "current_location_long": 79.8612
}
```

**Create Driver 2 (Kandy):**
```bash
POST http://localhost:8001/drivers
Content-Type: application/json

{
    "name": "Sarah Perera",
    "vehicle_number": "CBB-5678",
    "contact_number": "+94772345678",
    "current_location_lat": 7.2906,
    "current_location_long": 80.6337
}
```

### 2. Create Orders

**Order 1 (Galle):**
```bash
POST http://localhost:8001/orders
Content-Type: application/json

{
    "customer_id": 201,
    "product_name": "Mars Rover Kit",
    "quantity": 1,
    "address": "Galle, Sri Lanka"
}
```

**Order 2 (Jaffna):**
```bash
POST http://localhost:8001/orders
Content-Type: application/json

{
    "customer_id": 202,
    "product_name": "Oxygen Generator",
    "quantity": 2,
    "address": "Jaffna, Sri Lanka"
}
```

**Order 3 (Anuradhapura):**
```bash
POST http://localhost:8001/orders
Content-Type: application/json

{
    "customer_id": 203,
    "product_name": "Solar Panel Array",
    "quantity": 3,
    "address": "Anuradhapura, Sri Lanka"
}
```

### 3. Route Optimization

**Optimize Routes:**
```bash
POST http://localhost:8001/optimize-routes
Content-Type: application/json

{
    "order_ids": [1, 2, 3],
    "available_driver_ids": [1, 2]
}
```

**Response Example:**
```json
{
    "optimized_routes": [
        {
            "driver_id": 1,
            "driver_name": "John Silva",
            "assigned_orders": [
                {
                    "id": 1,
                    "customer_id": 201,
                    "product_name": "Mars Rover Kit",
                    "quantity": 1,
                    "address": "Galle, Sri Lanka",
                    "driver_id": 1,
                    "status": "assigned"
                },
                {
                    "id": 2,
                    "customer_id": 202,
                    "product_name": "Oxygen Generator",
                    "quantity": 2,
                    "address": "Jaffna, Sri Lanka",
                    "driver_id": 1,
                    "status": "assigned"
                }
            ],
            "total_distance": 506.73,
            "estimated_time": 10.13
        },
        {
            "driver_id": 2,
            "driver_name": "Sarah Perera",
            "assigned_orders": [
                {
                    "id": 3,
                    "customer_id": 203,
                    "product_name": "Solar Panel Array",
                    "quantity": 3,
                    "address": "Anuradhapura, Sri Lanka",
                    "driver_id": 2,
                    "status": "assigned"
                }
            ],
            "total_distance": 116.3,
            "estimated_time": 2.33
        }
    ],
    "total_orders_assigned": 3,
    "unassigned_orders": []
}
```

### 4. Query Operations

**Get All Drivers:**
```bash
GET http://localhost:8001/drivers
```

**Get All Orders:**
```bash
GET http://localhost:8001/orders
```

**Get Orders by Status:**
```bash
GET http://localhost:8001/orders?status=pending
```

**Get Driver's Orders:**
```bash
GET http://localhost:8001/drivers/1/orders
```

**Update Order Status:**
```bash
PUT http://localhost:8001/orders/1/status?status=in_transit
```

**Get Statistics:**
```bash
GET http://localhost:8001/statistics
```

## Route Optimization Algorithm

The service implements a simple but effective route optimization algorithm:

1. **Distance Calculation**: Uses Haversine formula for accurate distance calculation between coordinates
2. **Load Balancing**: Distributes orders evenly among available drivers
3. **Sequential Routing**: Calculates cumulative distance for each driver's route
4. **Time Estimation**: Estimates delivery time based on average speed (50 km/h)

### Supported Cities with Coordinates:
- Colombo: (6.9271, 79.8612)
- Kandy: (7.2906, 80.6337)
- Galle: (6.0535, 80.2210)
- Jaffna: (9.6615, 80.0255)
- Anuradhapura: (8.3114, 80.4037)
- Batticaloa: (7.7102, 81.6924)
- Ratnapura: (6.6828, 80.3992)
- Kurunegala: (7.4818, 80.3653)
- Badulla: (6.9934, 81.0550)
- Matara: (5.9549, 80.5550)

## Running the Service

### Using Docker Compose (Recommended)
```bash
docker-compose up --build -d ros
```

### Manual Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables:
   - `DATABASE_URL=postgresql://admin_user:admin_password@localhost:5432/ros_db`
3. Run: `uvicorn main:app --host 0.0.0.0 --port 8001`

## Service Integration

The ROS service is designed to integrate with other SwiftLogistics microservices:

- **CMS Integration**: Orders can be created from CMS and processed by ROS
- **Driver App Integration**: Drivers can receive optimized routes through mobile app
- **WMS Integration**: Warehouse management can coordinate with delivery schedules

## Monitoring and Health

- Health endpoint: `GET /health`
- Statistics endpoint: `GET /statistics`
- API Documentation: `http://localhost:8001/docs`
- OpenAPI Schema: `http://localhost:8001/openapi.json`

## Error Handling

The service implements comprehensive error handling:
- **400 Bad Request**: Invalid data or business rule violations
- **404 Not Found**: Resource doesn't exist
- **422 Validation Error**: Pydantic model validation failures
- **500 Internal Server Error**: Database or system errors

## Scalability Features

- **Database Connection Pooling**: Efficient database resource management
- **Pagination Support**: Handles large datasets efficiently
- **Async Processing**: Non-blocking operations for better performance
- **Container Ready**: Easy horizontal scaling with Docker/Kubernetes

## Security Considerations

- Input validation with Pydantic models
- SQL injection prevention with SQLAlchemy ORM
- Database connection retry logic
- Health check endpoints for monitoring

## Future Enhancements

1. **Advanced Routing**: Implement more sophisticated algorithms (TSP, genetic algorithms)
2. **Real-time Tracking**: GPS integration for live driver tracking
3. **Dynamic Routing**: Real-time route adjustments based on traffic
4. **Machine Learning**: Predictive delivery time estimation
5. **API Authentication**: JWT-based security implementation