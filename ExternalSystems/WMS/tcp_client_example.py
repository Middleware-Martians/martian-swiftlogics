#!/usr/bin/env python3
"""
WMS TCP Client Example
Demonstrates how to connect to the WMS TCP server and receive real-time updates
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WMSClient:
    def __init__(self, host='localhost', port=8003, client_type='TEST_CLIENT'):
        self.host = host
        self.port = port
        self.client_type = client_type
        self.client_id = f"{client_type}_{uuid.uuid4().hex[:8]}"
        self.reader = None
        self.writer = None
        self.running = False
    
    async def connect(self):
        """Connect to WMS TCP server"""
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.running = True
            logger.info(f"Connected to WMS server at {self.host}:{self.port}")
            
            # Start listening for messages
            asyncio.create_task(self.listen_for_messages())
            
            # Wait for welcome message
            await asyncio.sleep(1)
            
            # Send client identification
            await self.send_client_hello()
            
            # Start heartbeat
            asyncio.create_task(self.heartbeat_sender())
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from WMS server"""
        self.running = False
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        logger.info("Disconnected from WMS server")
    
    async def send_message(self, message: dict):
        """Send a message to the server"""
        try:
            message_json = json.dumps(message) + '\n'
            self.writer.write(message_json.encode('utf-8'))
            await self.writer.drain()
            logger.info(f"Sent: {message['message_type']}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def send_client_hello(self):
        """Send client identification"""
        message = {
            "message_id": f"hello_{uuid.uuid4().hex[:8]}",
            "message_type": "CLIENT_HELLO",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": self.client_id,
            "data": {
                "client_type": self.client_type,
                "client_id": self.client_id,
                "subscriptions": ["PACKAGE_RECEIVED", "PACKAGE_LOADED", "STATUS_UPDATE"]
            }
        }
        await self.send_message(message)
    
    async def heartbeat_sender(self):
        """Send periodic heartbeats"""
        while self.running:
            try:
                message = {
                    "message_id": f"hb_{uuid.uuid4().hex[:8]}",
                    "message_type": "HEARTBEAT",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "sender": self.client_id,
                    "data": {
                        "status": "alive"
                    }
                }
                await self.send_message(message)
                await asyncio.sleep(30)  # Send every 30 seconds
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                break
    
    async def listen_for_messages(self):
        """Listen for messages from the server"""
        while self.running:
            try:
                data = await self.reader.readline()
                if not data:
                    break
                
                message_text = data.decode('utf-8').strip()
                if message_text:
                    message = json.loads(message_text)
                    await self.handle_message(message)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
            except Exception as e:
                logger.error(f"Error reading message: {e}")
                break
    
    async def handle_message(self, message: dict):
        """Handle incoming messages from server"""
        message_type = message.get("message_type")
        timestamp = message.get("timestamp")
        data = message.get("data", {})
        
        logger.info(f"Received {message_type} at {timestamp}")
        
        if message_type == "WELCOME":
            logger.info(f"Welcome from WMS version {data.get('version')}")
            logger.info(f"Supported types: {data.get('supported_types')}")
            
        elif message_type == "CLIENT_ACK":
            logger.info(f"Authentication successful for {data.get('client_id')}")
            logger.info(f"Subscriptions: {data.get('subscriptions')}")
            
        elif message_type == "PACKAGE_RECEIVED":
            logger.info(f"📦 Package received: {data.get('order_number')} - {data.get('product_name')}")
            logger.info(f"   Customer: {data.get('customer_id')}, Quantity: {data.get('quantity')}")
            logger.info(f"   Location: {data.get('warehouse_location')}")
            
        elif message_type == "PACKAGE_LOADED":
            logger.info(f"🚛 Package loaded: {data.get('order_number')}")
            logger.info(f"   Driver: {data.get('driver_id')}, Vehicle: {data.get('vehicle_id')}")
            logger.info(f"   Loaded at: {data.get('loaded_at')}")
            
        elif message_type == "STATUS_UPDATE":
            logger.info(f"📝 Status update: {data.get('order_number')}")
            logger.info(f"   {data.get('old_status')} → {data.get('new_status')}")
            logger.info(f"   Updated by: {data.get('updated_by')}")
            
        elif message_type == "HEARTBEAT_ACK":
            logger.debug("Heartbeat acknowledged")
            
        else:
            logger.info(f"Unknown message type: {message_type}")

async def main():
    """Main function to run the client"""
    client = WMSClient(client_type='CMS_CLIENT')
    
    try:
        await client.connect()
        logger.info("Client connected and listening for messages...")
        logger.info("Press Ctrl+C to disconnect")
        
        # Keep the client running
        while client.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down client...")
    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())