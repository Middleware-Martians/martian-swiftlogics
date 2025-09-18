#!/usr/bin/env python3
"""
Simple TCP Test Script for WMS Real-time Messaging
This script demonstrates how to test the TCP messaging step by step
"""

import socket
import json
import time
import threading

def simple_tcp_test():
    """Simple synchronous TCP test"""
    print("🔌 Connecting to WMS TCP server...")
    
    try:
        # Connect to WMS TCP server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8003))
        print("✅ Connected to WMS TCP server at localhost:8003")
        
        # Send client identification
        client_hello = {
            "message_id": "test_001",
            "message_type": "CLIENT_HELLO",
            "timestamp": "2025-09-18T10:30:00Z",
            "sender": "TEST_CLIENT",
            "data": {
                "client_type": "TEST",
                "client_id": "test_client_001",
                "subscriptions": ["PACKAGE_RECEIVED", "PACKAGE_LOADED", "STATUS_UPDATE"]
            }
        }
        
        message = json.dumps(client_hello) + '\n'
        sock.send(message.encode('utf-8'))
        print("📤 Sent CLIENT_HELLO message")
        
        # Listen for messages
        print("👂 Listening for messages... (Press Ctrl+C to stop)")
        print("🔍 Now create orders in another terminal to see real-time updates!")
        print("")
        
        sock.settimeout(60)  # 60 second timeout
        
        while True:
            try:
                data = sock.recv(1024).decode('utf-8')
                if data:
                    lines = data.strip().split('\n')
                    for line in lines:
                        if line:
                            try:
                                message = json.loads(line)
                                message_type = message.get('message_type')
                                timestamp = message.get('timestamp')
                                msg_data = message.get('data', {})
                                
                                print(f"📨 Received: {message_type} at {timestamp}")
                                
                                if message_type == "WELCOME":
                                    print(f"   🎉 Welcome! Version: {msg_data.get('version')}")
                                    print(f"   📋 Supported types: {msg_data.get('supported_types')}")
                                
                                elif message_type == "CLIENT_ACK":
                                    print(f"   ✅ Authentication successful!")
                                    print(f"   📥 Subscriptions: {msg_data.get('subscriptions')}")
                                
                                elif message_type == "PACKAGE_RECEIVED":
                                    print(f"   📦 Package received: {msg_data.get('order_number')}")
                                    print(f"   🏷️  Product: {msg_data.get('product_name')}")
                                    print(f"   👤 Customer: {msg_data.get('customer_id')}")
                                    print(f"   📍 Location: {msg_data.get('warehouse_location')}")
                                
                                elif message_type == "PACKAGE_LOADED":
                                    print(f"   🚛 Package loaded: {msg_data.get('order_number')}")
                                    print(f"   🚗 Driver: {msg_data.get('driver_id')}")
                                    print(f"   🚐 Vehicle: {msg_data.get('vehicle_id')}")
                                
                                elif message_type == "STATUS_UPDATE":
                                    print(f"   📝 Status update: {msg_data.get('order_number')}")
                                    print(f"   🔄 {msg_data.get('old_status')} → {msg_data.get('new_status')}")
                                
                                print("")  # Empty line for readability
                                
                            except json.JSONDecodeError:
                                print(f"❌ Invalid JSON: {line}")
                
            except socket.timeout:
                print("⏰ No messages received in the last 60 seconds")
                break
            except Exception as e:
                print(f"❌ Error receiving data: {e}")
                break
    
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    
    finally:
        try:
            sock.close()
            print("🔌 Disconnected from WMS TCP server")
        except:
            pass

def create_test_order():
    """Create a test order via REST API to trigger TCP messages"""
    import requests
    
    print("\n🆕 Creating test order via REST API...")
    
    order_data = {
        "order_number": f"TCP_TEST_{int(time.time())}",
        "customer_id": 5001,
        "product_name": "TCP Test Product",
        "quantity": 1
    }
    
    try:
        response = requests.post(
            "http://localhost:8002/orders",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            order = response.json()
            print(f"✅ Order created: {order['order_number']} (ID: {order['id']})")
            return order['id']
        else:
            print(f"❌ Failed to create order: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return None

def assign_test_driver(order_id):
    """Assign a driver to test order"""
    import requests
    
    print(f"\n🚛 Assigning driver to order {order_id}...")
    
    try:
        response = requests.put(
            f"http://localhost:8002/warehouse/orders/{order_id}/assign-driver",
            json={"driver_id": 9001},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            order = response.json()
            print(f"✅ Driver assigned! Status: {order['status']}")
        else:
            print(f"❌ Failed to assign driver: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error assigning driver: {e}")

if __name__ == "__main__":
    print("🧪 WMS TCP Real-time Messaging Test")
    print("=" * 50)
    print("This script will:")
    print("1. Connect to WMS TCP server")
    print("2. Listen for real-time messages")
    print("3. You can create orders in another terminal to see live updates")
    print("")
    
    # Start TCP listener
    try:
        simple_tcp_test()
    except KeyboardInterrupt:
        print("\n⏹️  Test stopped by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")