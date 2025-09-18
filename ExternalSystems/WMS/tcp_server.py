import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Set, Optional
import weakref

logger = logging.getLogger(__name__)

class WMSClient:
    """Represents a connected client to the WMS TCP server"""
    
    def __init__(self, writer: asyncio.StreamWriter, client_id: str = None):
        self.writer = writer
        self.client_id = client_id or str(uuid.uuid4())
        self.client_type = "UNKNOWN"
        self.subscriptions: Set[str] = set()
        self.connected_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
        self.authenticated = False
    
    async def send_message(self, message: dict):
        """Send a message to this client"""
        try:
            message_json = json.dumps(message) + '\n'
            self.writer.write(message_json.encode('utf-8'))
            await self.writer.drain()
            return True
        except Exception as e:
            logger.error(f"Failed to send message to client {self.client_id}: {e}")
            return False
    
    def is_subscribed_to(self, message_type: str) -> bool:
        """Check if client is subscribed to a message type"""
        return message_type in self.subscriptions or not self.subscriptions
    
    def get_peer_info(self) -> str:
        """Get client connection information"""
        try:
            peername = self.writer.get_extra_info('peername')
            return f"{peername[0]}:{peername[1]}" if peername else "unknown"
        except:
            return "unknown"

class WMSTCPServer:
    """TCP server for WMS real-time messaging protocol"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8003):
        self.host = host
        self.port = port
        self.clients: Dict[str, WMSClient] = {}
        self.server: Optional[asyncio.Server] = None
        self.running = False
        self.message_queue = asyncio.Queue()
        
    async def start(self):
        """Start the TCP server"""
        try:
            self.server = await asyncio.start_server(
                self.handle_client, 
                self.host, 
                self.port
            )
            self.running = True
            
            # Start background tasks
            asyncio.create_task(self.heartbeat_monitor())
            asyncio.create_task(self.message_broadcaster())
            
            logger.info(f"WMS TCP Server started on {self.host}:{self.port}")
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"Failed to start TCP server: {e}")
            raise
    
    async def stop(self):
        """Stop the TCP server"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Close all client connections
        for client in list(self.clients.values()):
            await self.disconnect_client(client.client_id)
        
        logger.info("WMS TCP Server stopped")
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle new client connection"""
        client = WMSClient(writer)
        peer_info = client.get_peer_info()
        
        logger.info(f"New client connected from {peer_info}")
        
        try:
            # Send welcome message
            await self.send_welcome_message(client)
            
            # Handle client messages
            while self.running:
                try:
                    data = await asyncio.wait_for(reader.readline(), timeout=60.0)
                    if not data:
                        break
                    
                    message_text = data.decode('utf-8').strip()
                    if message_text:
                        await self.process_client_message(client, message_text)
                        
                except asyncio.TimeoutError:
                    logger.warning(f"Client {client.client_id} timed out")
                    break
                except Exception as e:
                    logger.error(f"Error handling client {client.client_id}: {e}")
                    break
        
        finally:
            await self.disconnect_client(client.client_id)
            logger.info(f"Client {client.client_id} disconnected")
    
    async def send_welcome_message(self, client: WMSClient):
        """Send welcome message to new client"""
        welcome_message = {
            "message_id": f"welcome_{uuid.uuid4().hex[:8]}",
            "message_type": "WELCOME",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": "WMS_001",
            "data": {
                "version": "1.0",
                "supported_types": [
                    "PACKAGE_RECEIVED", 
                    "PACKAGE_LOADED", 
                    "STATUS_UPDATE",
                    "HEARTBEAT"
                ],
                "heartbeat_interval": 30,
                "client_id": client.client_id
            }
        }
        await client.send_message(welcome_message)
    
    async def process_client_message(self, client: WMSClient, message_text: str):
        """Process incoming message from client"""
        try:
            message = json.loads(message_text)
            message_type = message.get("message_type")
            
            if message_type == "CLIENT_HELLO":
                await self.handle_client_hello(client, message)
            elif message_type == "HEARTBEAT":
                await self.handle_heartbeat(client, message)
            elif message_type == "SUBSCRIBE":
                await self.handle_subscription(client, message)
            else:
                logger.warning(f"Unknown message type from {client.client_id}: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client.client_id}: {message_text}")
        except Exception as e:
            logger.error(f"Error processing message from {client.client_id}: {e}")
    
    async def handle_client_hello(self, client: WMSClient, message: dict):
        """Handle client identification message"""
        data = message.get("data", {})
        client.client_type = data.get("client_type", "UNKNOWN")
        client.subscriptions = set(data.get("subscriptions", []))
        client.authenticated = True
        
        # Add to clients list
        self.clients[client.client_id] = client
        
        # Send confirmation
        response = {
            "message_id": f"ack_{uuid.uuid4().hex[:8]}",
            "message_type": "CLIENT_ACK",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": "WMS_001",
            "data": {
                "status": "authenticated",
                "client_id": client.client_id,
                "subscriptions": list(client.subscriptions)
            }
        }
        await client.send_message(response)
        
        logger.info(f"Client {client.client_id} authenticated as {client.client_type}")
    
    async def handle_heartbeat(self, client: WMSClient, message: dict):
        """Handle client heartbeat"""
        client.last_heartbeat = datetime.utcnow()
        
        # Send heartbeat response
        response = {
            "message_id": f"hb_ack_{uuid.uuid4().hex[:8]}",
            "message_type": "HEARTBEAT_ACK",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": "WMS_001",
            "data": {
                "status": "alive"
            }
        }
        await client.send_message(response)
    
    async def handle_subscription(self, client: WMSClient, message: dict):
        """Handle subscription updates"""
        data = message.get("data", {})
        action = data.get("action", "subscribe")
        message_types = data.get("message_types", [])
        
        if action == "subscribe":
            client.subscriptions.update(message_types)
        elif action == "unsubscribe":
            client.subscriptions.difference_update(message_types)
        
        logger.info(f"Client {client.client_id} updated subscriptions: {client.subscriptions}")
    
    async def disconnect_client(self, client_id: str):
        """Disconnect a client"""
        if client_id in self.clients:
            client = self.clients[client_id]
            try:
                client.writer.close()
                await client.writer.wait_closed()
            except:
                pass
            del self.clients[client_id]
    
    async def heartbeat_monitor(self):
        """Monitor client heartbeats and disconnect stale clients"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                stale_clients = []
                
                for client_id, client in self.clients.items():
                    time_since_heartbeat = (current_time - client.last_heartbeat).total_seconds()
                    if time_since_heartbeat > 90:  # 90 seconds timeout
                        stale_clients.append(client_id)
                
                for client_id in stale_clients:
                    logger.warning(f"Client {client_id} heartbeat timeout, disconnecting")
                    await self.disconnect_client(client_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(30)
    
    async def message_broadcaster(self):
        """Broadcast messages to subscribed clients"""
        while self.running:
            try:
                # Get message from queue
                message = await self.message_queue.get()
                message_type = message.get("message_type")
                
                # Broadcast to subscribed clients
                clients_to_remove = []
                for client_id, client in self.clients.items():
                    if client.is_subscribed_to(message_type):
                        success = await client.send_message(message)
                        if not success:
                            clients_to_remove.append(client_id)
                
                # Remove failed clients
                for client_id in clients_to_remove:
                    await self.disconnect_client(client_id)
                
            except Exception as e:
                logger.error(f"Error in message broadcaster: {e}")
                await asyncio.sleep(1)
    
    async def broadcast_message(self, message_type: str, data: dict):
        """Queue a message for broadcasting"""
        message = {
            "message_id": f"wms_{uuid.uuid4().hex[:8]}",
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": "WMS_001",
            "data": data
        }
        await self.message_queue.put(message)
    
    def get_connected_clients(self) -> Dict[str, dict]:
        """Get information about connected clients"""
        return {
            client_id: {
                "client_type": client.client_type,
                "connected_at": client.connected_at.isoformat(),
                "last_heartbeat": client.last_heartbeat.isoformat(),
                "subscriptions": list(client.subscriptions),
                "peer_info": client.get_peer_info()
            }
            for client_id, client in self.clients.items()
        }

# Global TCP server instance
tcp_server: Optional[WMSTCPServer] = None

async def start_tcp_server():
    """Start the global TCP server"""
    global tcp_server
    if tcp_server is None:
        tcp_server = WMSTCPServer()
        await tcp_server.start()

async def stop_tcp_server():
    """Stop the global TCP server"""
    global tcp_server
    if tcp_server:
        await tcp_server.stop()
        tcp_server = None

def get_tcp_server() -> Optional[WMSTCPServer]:
    """Get the global TCP server instance"""
    return tcp_server

async def broadcast_package_received(package_data: dict):
    """Broadcast package received event"""
    if tcp_server:
        await tcp_server.broadcast_message("PACKAGE_RECEIVED", package_data)

async def broadcast_package_loaded(package_data: dict):
    """Broadcast package loaded event"""
    if tcp_server:
        await tcp_server.broadcast_message("PACKAGE_LOADED", package_data)

async def broadcast_status_update(status_data: dict):
    """Broadcast status update event"""
    if tcp_server:
        await tcp_server.broadcast_message("STATUS_UPDATE", status_data)