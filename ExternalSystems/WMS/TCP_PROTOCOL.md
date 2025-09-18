# WMS TCP/IP Protocol Implementation

## Overview
The WMS implements a proprietary messaging protocol over TCP/IP for real-time warehouse updates, alongside REST APIs for management operations.

## Architecture
```
┌─────────────┐    TCP/IP     ┌─────────────┐    HTTP/REST    ┌─────────────┐
│   Client    │◄─────────────►│     WMS     │◄───────────────►│  Dashboard  │
│  Systems    │   Messages    │   Server    │   Management    │   / Admin   │
└─────────────┘               └─────────────┘                 └─────────────┘
```

## TCP/IP Protocol Specification

### Connection Details
- **Port**: 8003 (TCP Server)
- **Protocol**: Custom binary/JSON over TCP
- **Connection**: Persistent connections with heartbeat
- **Encoding**: UTF-8 JSON messages

### Message Format
```json
{
    "message_id": "unique_identifier",
    "message_type": "PACKAGE_RECEIVED|PACKAGE_LOADED|STATUS_UPDATE|HEARTBEAT",
    "timestamp": "2025-09-18T10:30:00Z",
    "sender": "WMS_001",
    "data": {
        // Message-specific payload
    }
}
```

## Message Types

### 1. Package Received
**Sent when**: Package arrives at warehouse
```json
{
    "message_id": "msg_001",
    "message_type": "PACKAGE_RECEIVED",
    "timestamp": "2025-09-18T10:30:00Z",
    "sender": "WMS_001",
    "data": {
        "package_id": "PKG_12345",
        "order_number": "WMS001",
        "customer_id": 1001,
        "product_name": "Laptop Computer",
        "quantity": 2,
        "received_at": "2025-09-18T10:30:00Z",
        "warehouse_location": "A-1-B"
    }
}
```

### 2. Package Loaded
**Sent when**: Package loaded onto vehicle
```json
{
    "message_id": "msg_002",
    "message_type": "PACKAGE_LOADED",
    "timestamp": "2025-09-18T12:15:00Z",
    "sender": "WMS_001",
    "data": {
        "package_id": "PKG_12345",
        "driver_id": 2001,
        "vehicle_id": "VEH_501",
        "loaded_at": "2025-09-18T12:15:00Z",
        "estimated_delivery": "2025-09-18T16:00:00Z"
    }
}
```

### 3. Status Update
**Sent when**: Package status changes
```json
{
    "message_id": "msg_003",
    "message_type": "STATUS_UPDATE",
    "timestamp": "2025-09-18T11:45:00Z",
    "sender": "WMS_001",
    "data": {
        "package_id": "PKG_12345",
        "old_status": "received",
        "new_status": "in_warehouse",
        "location": "A-1-B",
        "updated_by": "operator_123"
    }
}
```

### 4. Heartbeat
**Sent**: Every 30 seconds to maintain connection
```json
{
    "message_id": "hb_001",
    "message_type": "HEARTBEAT",
    "timestamp": "2025-09-18T10:30:00Z",
    "sender": "WMS_001",
    "data": {
        "status": "operational",
        "active_packages": 45,
        "last_activity": "2025-09-18T10:29:45Z"
    }
}
```

## Client Protocol

### Connection Handshake
1. Client connects to WMS on port 8003
2. WMS sends welcome message
3. Client sends identification
4. WMS confirms and starts sending updates

### Welcome Message
```json
{
    "message_id": "welcome_001",
    "message_type": "WELCOME",
    "timestamp": "2025-09-18T10:30:00Z",
    "sender": "WMS_001",
    "data": {
        "version": "1.0",
        "supported_types": ["PACKAGE_RECEIVED", "PACKAGE_LOADED", "STATUS_UPDATE"],
        "heartbeat_interval": 30
    }
}
```

### Client Identification
```json
{
    "message_id": "client_001",
    "message_type": "CLIENT_HELLO",
    "timestamp": "2025-09-18T10:30:05Z",
    "sender": "CMS_CLIENT",
    "data": {
        "client_type": "CMS",
        "client_id": "cms_001",
        "subscriptions": ["PACKAGE_RECEIVED", "STATUS_UPDATE"]
    }
}
```

## Implementation Plan

### Phase 1: TCP Server Setup ✅
- [x] Create async TCP server on port 8003
- [x] Handle multiple client connections
- [x] Message parsing and validation
- [x] Connection management with heartbeat

### Phase 2: Message Broadcasting 🚧
- [ ] Real-time message broadcasting to connected clients
- [ ] Client subscription management
- [ ] Message queuing for disconnected clients
- [ ] Error handling and reconnection logic

### Phase 3: Integration 🔄
- [ ] Integrate with existing REST API
- [ ] Database event triggers for TCP messages
- [ ] Performance optimization
- [ ] Monitoring and logging

## Usage Examples

### For CMS Integration
```python
import socket
import json

# Connect to WMS TCP server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8003))

# Send client identification
client_hello = {
    "message_id": "cms_hello_001",
    "message_type": "CLIENT_HELLO",
    "timestamp": "2025-09-18T10:30:00Z",
    "sender": "CMS_CLIENT",
    "data": {
        "client_type": "CMS",
        "client_id": "cms_001",
        "subscriptions": ["PACKAGE_RECEIVED", "STATUS_UPDATE"]
    }
}
sock.send(json.dumps(client_hello).encode() + b'\n')

# Listen for messages
while True:
    data = sock.recv(1024).decode()
    message = json.loads(data)
    print(f"Received: {message['message_type']}")
```

### For ROS Integration
```python
# Similar connection but subscribe to different events
subscriptions = ["PACKAGE_LOADED", "STATUS_UPDATE"]
# Process driver assignment and route optimization
```

## Security Considerations

### Authentication
- Client certificates for secure connections
- API keys for client identification
- IP whitelisting for trusted systems

### Data Protection
- Message encryption for sensitive data
- Audit logging for all communications
- Rate limiting to prevent abuse

## Performance Metrics

### Target Performance
- **Connection Setup**: < 100ms
- **Message Delivery**: < 50ms
- **Concurrent Connections**: 100+
- **Messages/Second**: 1000+
- **Uptime**: 99.9%

### Monitoring
- Connection count and status
- Message throughput and latency
- Error rates and reconnections
- Memory and CPU usage

Would you like me to implement the full TCP/IP server alongside the existing REST API?