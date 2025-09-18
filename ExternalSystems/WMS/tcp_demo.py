#!/usr/bin/env python3
"""
Quick TCP Demo Script
Demonstrates TCP real-time messaging with automatic order creation
"""

import socket
import json
import threading
import time
import requests

def tcp_listener():
    """Listen for TCP messages"""
    print("🔌 Connecting to WMS TCP server...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8003))
        print("✅ Connected to WMS TCP server")
        
        # Send client hello
        client_hello = {
            "message_type": "CLIENT_HELLO",
            "sender": "DEMO_CLIENT",
            "data": {
                "client_type": "DEMO",
                "subscriptions": ["PACKAGE_RECEIVED", "PACKAGE_LOADED", "STATUS_UPDATE"]
            }
        }
        
        sock.send((json.dumps(client_hello) + '\n').encode('utf-8'))
        print("📤 Sent CLIENT_HELLO")
        
        # Listen for messages
        sock.settimeout(1)
        messages_received = 0
        
        while messages_received < 10:  # Listen for up to 10 messages
            try:
                data = sock.recv(1024).decode('utf-8')
                if data:
                    lines = data.strip().split('\n')
                    for line in lines:
                        if line:
                            try:
                                message = json.loads(line)
                                message_type = message.get('message_type')
                                msg_data = message.get('data', {})
                                
                                print(f"\n📨 {message_type}")
                                
                                if message_type == "PACKAGE_RECEIVED":
                                    print(f"   📦 Order: {msg_data.get('order_number')}")
                                    print(f"   🏷️  Product: {msg_data.get('product_name')}")
                                    
                                elif message_type == "PACKAGE_LOADED":
                                    print(f"   🚛 Order: {msg_data.get('order_number')}")
                                    print(f"   🚗 Driver: {msg_data.get('driver_id')}")
                                
                                messages_received += 1
                                
                            except json.JSONDecodeError:
                                pass
            
            except socket.timeout:
                continue
            except Exception as e:
                break
        
        sock.close()
        print("\n✅ TCP demo completed")
        
    except Exception as e:
        print(f"❌ TCP connection failed: {e}")

def create_demo_orders():
    """Create demo orders to trigger TCP messages"""
    time.sleep(2)  # Wait for TCP connection
    
    print("\n🚀 Creating demo orders...")
    
    # Create first order
    order1 = {
        "order_number": f"DEMO_{int(time.time())}_1",
        "customer_id": 7001,
        "product_name": "Demo Product 1",
        "quantity": 1
    }
    
    try:
        response = requests.post(
            "http://localhost:8002/orders",
            json=order1,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            order = response.json()
            print(f"✅ Created order: {order['order_number']}")
            
            # Wait a moment then assign driver
            time.sleep(2)
            
            # Assign driver
            driver_response = requests.put(
                f"http://localhost:8002/warehouse/orders/{order['id']}/assign-driver",
                json={"driver_id": 8001},
                headers={"Content-Type": "application/json"}
            )
            
            if driver_response.status_code == 200:
                print(f"✅ Assigned driver to order {order['id']}")
            
        else:
            print(f"❌ Failed to create order: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error creating order: {e}")

if __name__ == "__main__":
    print("🧪 WMS TCP Real-time Messaging Demo")
    print("=" * 50)
    
    # Start TCP listener in background
    tcp_thread = threading.Thread(target=tcp_listener)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    # Create orders to trigger messages
    order_thread = threading.Thread(target=create_demo_orders)
    order_thread.daemon = True
    order_thread.start()
    
    # Wait for threads to complete
    tcp_thread.join(timeout=15)
    order_thread.join(timeout=10)
    
    print("\n🎉 Demo completed!")