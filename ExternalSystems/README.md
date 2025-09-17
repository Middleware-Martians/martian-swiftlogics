# SwiftLogistics External Systems

This directory contains the external systems for the SwiftLogistics project, including the CMS (Client Management System) and supporting database infrastructure.

## Services

### PostgreSQL Database
- **Container**: `swiftlogistics_postgres`
- **Port**: `5432`
- **Databases**: `cms_db`, `ros_db`, `wms_db`
- **Admin User**: `admin_user` / `admin_password`

### CMS Service (Client Management System)
- **Container**: `swiftlogistics_cms`
- **Port**: `8000`
- **Technology**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL (`cms_db`)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Ports 5432 and 8000 available

### Running the Services

#### Option 1: Using the startup scripts
```bash
# On Windows
start.bat

# On Linux/Mac
./start.sh
```

#### Option 2: Manual Docker Compose
```bash
docker-compose up --build -d
```

### Stopping the Services
```bash
docker-compose down
```

## API Documentation

Once the services are running, you can access:

- **CMS API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Available Endpoints

#### Health Check
```
GET /health
```

#### Orders Management
```
POST /orders          # Create a new order
GET /orders           # Get all orders
GET /orders/{id}      # Get specific order
PUT /orders/{id}      # Update order
DELETE /orders/{id}   # Delete order
```

#### Example Order Creation
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "product_name": "Test Product", "quantity": 5}'
```

Or using PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/orders" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"customer_id": 1, "product_name": "Test Product", "quantity": 5}'
```

## Database Setup

The system automatically creates the following databases and users:
- `cms_db` with `cms_user`
- `ros_db` with `ros_user` 
- `wms_db` with `wms_user`

The CMS service currently uses the admin user (`admin_user`) for full database access.

## Troubleshooting

### Check service status
```bash
docker-compose ps
```

### View logs
```bash
docker-compose logs -f cms      # CMS service logs
docker-compose logs -f postgres # Database logs
```

### Reset everything
```bash
docker-compose down
docker volume prune -f
docker-compose up --build -d
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   CMS Service   │────│  PostgreSQL DB  │
│   (Port 8000)   │    │   (Port 5432)   │
│   FastAPI       │    │   cms_db        │
└─────────────────┘    │   ros_db        │
                       │   wms_db        │
                       └─────────────────┘
```

## Future Development

The ROS and WMS services can be implemented following the same pattern:
1. Create Python service in respective folders
2. Add Dockerfile and requirements.txt
3. Update docker-compose.yml to include the new services
4. Use the respective database connections (ros_db, wms_db)