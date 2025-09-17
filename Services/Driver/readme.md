# Driver Microservice

A Spring Boot microservice for managing drivers in the Martian SwiftLogics system.

## Features

- Complete CRUD operations for drivers
- Driver status management (ONLINE, OFFLINE, BUSY, ON_DELIVERY)
- Location tracking with GPS coordinates
- Search drivers by proximity using geographical calculations
- Vehicle type and license number management
- REST API with comprehensive endpoints
- PostgreSQL database integration
- Spring Boot Actuator for health monitoring
- Kafka integration for event publishing

## Technology Stack

- **Framework**: Spring Boot 3.1.0
- **Database**: PostgreSQL (with H2 for testing)
- **Messaging**: Apache Kafka
- **Testing**: JUnit 5, MockMvc
- **Build Tool**: Maven
- **Java Version**: 17

## API Endpoints

### Driver Management
- `GET /api/drivers` - Get all drivers
- `GET /api/drivers/{id}` - Get driver by ID
- `GET /api/drivers/license/{licenseNumber}` - Get driver by license number
- `POST /api/drivers` - Create new driver
- `PUT /api/drivers/{id}` - Update driver
- `DELETE /api/drivers/{id}` - Delete driver

### Driver Operations
- `PUT /api/drivers/{id}/status` - Update driver status
- `PUT /api/drivers/{id}/location` - Update driver location
- `GET /api/drivers/status/{status}` - Get drivers by status
- `GET /api/drivers/nearby?latitude={lat}&longitude={lon}&radiusKm={radius}` - Find nearby drivers
- `GET /api/drivers/vehicle-type/{type}` - Get drivers by vehicle type

### Monitoring
- `GET /api/drivers/health` - Health check

## Database Schema

The `drivers` table includes:
- `id` (Primary Key)
- `name` (Required)
- `license_number` (Required, Unique)
- `phone_number` (Required)
- `email`
- `vehicle_type`
- `vehicle_number`
- `status` (ENUM: ONLINE, OFFLINE, BUSY, ON_DELIVERY)
- `current_latitude`
- `current_longitude`
- `last_location_update`
- `created_at`
- `updated_at`

## Setup Instructions

### Prerequisites
1. Java 17 or higher
2. Maven 3.6+
3. PostgreSQL 12+
4. Apache Kafka (optional, for messaging)

### Database Setup
1. Create PostgreSQL database:
   ```sql
   CREATE DATABASE driver_db;
   CREATE USER driver_user WITH PASSWORD 'driver_password';
   GRANT ALL PRIVILEGES ON DATABASE driver_db TO driver_user;
   ```

### Configuration
1. Update `src/main/resources/application.yml` with your database credentials:
   ```yaml
   spring:
     datasource:
       url: jdbc:postgresql://localhost:5432/driver_db
       username: driver_user
       password: driver_password
   ```

### Running the Application

1. **Build the project**:
   ```bash
   mvn clean install
   ```

2. **Run with Maven**:
   ```bash
   mvn spring-boot:run
   ```

3. **Run with Java**:
   ```bash
   java -jar target/driver-service-0.0.1-SNAPSHOT.jar
   ```

4. **Run tests**:
   ```bash
   mvn test
   ```

The application will start on port 8080 with context path `/driver-service`.

### Docker Setup (Optional)

Create a `Dockerfile`:
```dockerfile
FROM openjdk:17-jdk-slim
VOLUME /tmp
COPY target/driver-service-0.0.1-SNAPSHOT.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]
```

## Environment Variables

- `DB_USERNAME` - Database username (default: driver_user)
- `DB_PASSWORD` - Database password (default: driver_password)
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka servers (default: localhost:9092)

## Example Usage

### Create a Driver
```bash
curl -X POST http://localhost:8080/driver-service/api/drivers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "licenseNumber": "DL123456",
    "phoneNumber": "+1234567890",
    "email": "john.doe@email.com",
    "vehicleType": "Car",
    "vehicleNumber": "ABC123"
  }'
```

### Update Driver Status
```bash
curl -X PUT http://localhost:8080/driver-service/api/drivers/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "ONLINE"}'
```

### Update Driver Location
```bash
curl -X PUT http://localhost:8080/driver-service/api/drivers/1/location \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060}'
```

### Find Nearby Drivers
```bash
curl "http://localhost:8080/driver-service/api/drivers/nearby?latitude=40.7128&longitude=-74.0060&radiusKm=5"
```

## Health Monitoring

- Application health: `http://localhost:8080/driver-service/actuator/health`
- Service health: `http://localhost:8080/driver-service/api/drivers/health`

## Future Enhancements

- Real-time location tracking with WebSocket
- Driver ratings and reviews
- Route optimization integration
- Advanced search filters
- Performance metrics and analytics
- Integration with external mapping services
