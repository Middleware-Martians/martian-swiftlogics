# WMS (Warehouse Management System) Mock Service

This is a mock implementation of the Warehouse Management System service that simulates warehouse dispatch instructions and acknowledgment over TCP/IP, as specified in the implementation guide.

## Features

- TCP server on port 5000 that accepts JSON dispatch messages
- HTTP API on port 5001 for inventory and dispatch monitoring
- In-memory database with sample inventory
- Proper error handling and validation
- Docker-based deployment for easy testing

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Rust (optional, only for local development)

### Running the Service

Use the provided script to manage the service:

```bash
# Start the service
./start_docker.sh start

# Check the status
./start_docker.sh status

# View the logs
./start_docker.sh logs

# Stop the service
./start_docker.sh stop
```

## API Endpoints

The service provides the following HTTP API endpoints:

- `GET /inventory` - List all inventory items
- `GET /inventory/:item_id` - Get details for a specific inventory item
- `GET /dispatches` - List all dispatches

## Testing the TCP Server

You can test the TCP server using telnet or netcat:

```bash
# Using netcat
echo '{"order_id": 1001, "items": [{"item_id": 1, "quantity": 2}, {"item_id": 2, "quantity": 1}]}' | nc localhost 5000

# Using telnet
telnet localhost 5000
```

Then input the JSON:
```json
{"order_id": 1001, "items": [{"item_id": 1, "quantity": 2}, {"item_id": 2, "quantity": 1}]}
```

## Expected Response

```json
{"status":"WMS_OK","message":"Dispatch received"}
```

## Architecture

- The system is built using Rust and the Tokio async runtime
- TCP server handles dispatch requests from external systems
- HTTP API provides additional monitoring capabilities
- In-memory database simulates inventory management

## Development

For local development:

```bash
cd mock-wms
cargo run
```

## Environment Variables

- `RUST_LOG` - Log level (default: info)
- `WMS_PORT` - TCP server port (default: 5000)
