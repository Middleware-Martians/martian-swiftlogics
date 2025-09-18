# WMS TCP Real-time Messaging Testing Guide

## 🧪 How to Test TCP Real-time Messaging

This guide shows you multiple ways to test the WMS TCP real-time messaging functionality.

## Method 1: Simple Python TCP Test (Recommended)

### Step 1: Start the TCP Test Client
```bash
cd ExternalSystems/WMS
python simple_tcp_test.py
```

### Step 2: In Another Terminal, Create Orders
```powershell
# Create an order to trigger PACKAGE_RECEIVED
$body = @{
    order_number = "TCP_TEST_001"
    customer_id = 1001
    product_name = "Test Product"
    quantity = 2
} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8002/orders -Method POST -Body $body -ContentType "application/json"
```

### Step 3: Assign a Driver to Trigger More Events
```powershell
# This will trigger PACKAGE_LOADED and STATUS_UPDATE
$body = @{ driver_id = 2001 } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8002/warehouse/orders/1/assign-driver -Method PUT -Body $body -ContentType "application/json"
```

### Expected Output in TCP Client:
```
📨 Received: WELCOME at 2025-09-18T10:30:00Z
   🎉 Welcome! Version: 1.0
   📋 Supported types: ['PACKAGE_RECEIVED', 'PACKAGE_LOADED', 'STATUS_UPDATE']

📨 Received: CLIENT_ACK at 2025-09-18T10:30:01Z
   ✅ Authentication successful!
   📥 Subscriptions: ['PACKAGE_RECEIVED', 'PACKAGE_LOADED', 'STATUS_UPDATE']

📨 Received: PACKAGE_RECEIVED at 2025-09-18T10:30:15Z
   📦 Package received: TCP_TEST_001
   🏷️  Product: Test Product
   👤 Customer: 1001
   📍 Location: WH-1-A

📨 Received: PACKAGE_LOADED at 2025-09-18T10:30:30Z
   🚛 Package loaded: TCP_TEST_001
   🚗 Driver: 2001
   🚐 Vehicle: VEH_2001

📨 Received: STATUS_UPDATE at 2025-09-18T10:30:30Z
   📝 Status update: TCP_TEST_001
   🔄 received → loaded
```

## Method 2: Advanced Async Client

### Use the Full-Featured Client
```bash
cd ExternalSystems/WMS
python tcp_client_example.py
```

This client includes:
- Automatic heartbeat management
- Connection recovery
- Detailed message logging
- Subscription management

## Method 3: Manual Testing with Telnet

### Connect with Telnet (Windows)
```cmd
telnet localhost 8003
```

### Send Manual Messages
```json
{"message_type":"CLIENT_HELLO","sender":"MANUAL_TEST","data":{"client_type":"MANUAL","subscriptions":["PACKAGE_RECEIVED"]}}
```

## Method 4: PowerShell TCP Client

### Simple PowerShell TCP Test
```powershell
# Create TCP connection
$tcpClient = New-Object System.Net.Sockets.TcpClient
$tcpClient.Connect("localhost", 8003)
$stream = $tcpClient.GetStream()

# Send client hello
$message = '{"message_type":"CLIENT_HELLO","sender":"PS_TEST","data":{"client_type":"POWERSHELL","subscriptions":["PACKAGE_RECEIVED"]}}'
$data = [System.Text.Encoding]::UTF8.GetBytes($message + "`n")
$stream.Write($data, 0, $data.Length)

# Read welcome message
$buffer = New-Object byte[] 1024
$bytesRead = $stream.Read($buffer, 0, 1024)
$response = [System.Text.Encoding]::UTF8.GetString($buffer, 0, $bytesRead)
Write-Host "Received: $response"

# Keep connection open to receive messages
# (Create orders in another terminal)

# Close connection
$tcpClient.Close()
```

## Test Scenarios

### Scenario 1: Package Lifecycle Test
```bash
# Terminal 1: Start TCP client
python simple_tcp_test.py

# Terminal 2: Create order (triggers PACKAGE_RECEIVED)
curl -X POST http://localhost:8002/orders \
  -H "Content-Type: application/json" \
  -d '{"order_number":"LIFECYCLE_001","customer_id":1001,"product_name":"Lifecycle Test","quantity":1}'

# Terminal 2: Assign driver (triggers PACKAGE_LOADED + STATUS_UPDATE)
curl -X PUT http://localhost:8002/warehouse/orders/1/assign-driver \
  -H "Content-Type: application/json" \
  -d '{"driver_id":2001}'

# Terminal 2: Update status (triggers STATUS_UPDATE)
curl -X PUT http://localhost:8002/warehouse/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"delivered"}'
```

### Scenario 2: Multiple Client Test
```bash
# Terminal 1: Start CMS client
python -c "
import asyncio
from tcp_client_example import WMSClient

async def test():
    client = WMSClient(client_type='CMS_CLIENT')
    await client.connect()
    await asyncio.sleep(60)

asyncio.run(test())
"

# Terminal 2: Start ROS client  
python -c "
import asyncio
from tcp_client_example import WMSClient

async def test():
    client = WMSClient(client_type='ROS_CLIENT')
    await client.connect()
    await asyncio.sleep(60)

asyncio.run(test())
"

# Terminal 3: Create orders and see both clients receive messages
```

### Scenario 3: Stress Test
```bash
# Create multiple orders rapidly
for i in {1..10}; do
  curl -X POST http://localhost:8002/orders \
    -H "Content-Type: application/json" \
    -d "{\"order_number\":\"STRESS_$i\",\"customer_id\":$((1000+i)),\"product_name\":\"Stress Test $i\",\"quantity\":$i}"
  sleep 1
done
```

## Verification Commands

### Check TCP Server Status
```bash
curl http://localhost:8002/tcp-status
```

### Check Connected Clients
```bash
curl http://localhost:8002/tcp-status | jq '.clients'
```

### Monitor Server Logs
```bash
docker-compose logs -f wms
```

## Common Issues and Solutions

### Issue 1: Connection Refused
**Problem**: Can't connect to port 8003
**Solution**: 
```bash
# Check if WMS is running
curl http://localhost:8002/health

# Check if TCP server is running
curl http://localhost:8002/tcp-status

# Restart services
docker-compose restart wms
```

### Issue 2: No Messages Received
**Problem**: Connected but no messages coming through
**Solution**:
```bash
# Check client authentication
# Ensure CLIENT_HELLO was sent correctly

# Check subscriptions
# Verify client subscribed to correct message types

# Test with simple order creation
curl -X POST http://localhost:8002/orders \
  -H "Content-Type: application/json" \
  -d '{"order_number":"DEBUG_001","customer_id":1001,"product_name":"Debug","quantity":1}'
```

### Issue 3: JSON Parse Errors
**Problem**: Invalid JSON in TCP messages
**Solution**:
```bash
# Ensure messages end with \n
# Check message format matches protocol spec
# Use simple_tcp_test.py for debugging
```

## Performance Testing

### Measure Message Latency
```python
import time
import asyncio
from tcp_client_example import WMSClient

async def latency_test():
    client = WMSClient(client_type='LATENCY_TEST')
    await client.connect()
    
    # Record time when creating order
    start_time = time.time()
    
    # Create order via REST API
    # ... (create order code)
    
    # Measure time until TCP message received
    # ... (in message handler)
```

### Load Testing
```bash
# Use Apache Bench to create orders rapidly
ab -n 100 -c 10 -p order_data.json -T application/json http://localhost:8002/orders
```

## Integration Examples

### CMS Integration Example
```python
class CMSIntegration:
    async def connect_to_wms(self):
        self.wms_client = WMSClient(client_type='CMS')
        await self.wms_client.connect()
    
    async def handle_package_received(self, data):
        # Update customer notification
        customer_id = data['customer_id']
        order_number = data['order_number']
        await self.notify_customer(customer_id, f"Order {order_number} received at warehouse")
```

### ROS Integration Example
```python
class ROSIntegration:
    async def connect_to_wms(self):
        self.wms_client = WMSClient(client_type='ROS')
        await self.wms_client.connect()
    
    async def handle_package_loaded(self, data):
        # Optimize route for driver
        driver_id = data['driver_id']
        order_number = data['order_number']
        await self.optimize_route(driver_id, order_number)
```

## Summary

The WMS TCP real-time messaging can be tested using:

1. ✅ **Simple Python client** - `simple_tcp_test.py` (easiest)
2. ✅ **Full async client** - `tcp_client_example.py` (production-like)
3. ✅ **Manual testing** - telnet/PowerShell (debugging)
4. ✅ **Integration testing** - multiple clients (realistic scenarios)

Choose the method that best fits your testing needs!