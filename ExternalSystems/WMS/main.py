from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
import time
import sys
import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager

# Import TCP server
from tcp_server import (
    start_tcp_server, 
    stop_tcp_server, 
    get_tcp_server,
    broadcast_package_received,
    broadcast_package_loaded,
    broadcast_status_update
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "postgresql://admin_user:admin_password@postgres:5432/wms_db"

# Retry logic for database connection
def create_engine_with_retry():
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Test the connection
            engine.connect()
            return engine
        except Exception as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries exceeded. Exiting.")
                sys.exit(1)

engine = create_engine_with_retry()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, index=True, nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    driver_id = Column(Integer, nullable=True)
    status = Column(String, default="received", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic Models
class OrderCreate(BaseModel):
    order_number: str
    customer_id: int
    product_name: str
    quantity: int
    driver_id: Optional[int] = None
    status: Optional[str] = "received"

class OrderUpdate(BaseModel):
    order_number: Optional[str] = None
    customer_id: Optional[int] = None
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    driver_id: Optional[int] = None
    status: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    product_name: str
    quantity: int
    driver_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrderReceive(BaseModel):
    order_number: str
    customer_id: int
    product_name: str
    quantity: int

class DriverAssignment(BaseModel):
    driver_id: int

class StatusUpdate(BaseModel):
    status: str

# Create tables with retry logic
def create_tables_with_retry():
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("WMS Tables created successfully!")
            return
        except Exception as e:
            print(f"Table creation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries exceeded for table creation. Tables may need to be created manually.")

create_tables_with_retry()

# Lifespan manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start TCP server
    logger.info("Starting WMS TCP server...")
    tcp_task = asyncio.create_task(start_tcp_server())
    try:
        yield
    finally:
        # Shutdown: Stop TCP server
        logger.info("Stopping WMS TCP server...")
        tcp_task.cancel()
        await stop_tcp_server()

# FastAPI app with lifespan
app = FastAPI(
    title="WMS Service", 
    description="Warehouse Management System API for SwiftLogistics",
    version="1.0.0",
    lifespan=lifespan
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility function to validate status
def validate_status(status: str) -> bool:
    valid_statuses = ["received", "in_warehouse", "loaded", "delivered"]
    return status in valid_statuses

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "WMS", 
        "timestamp": datetime.now().isoformat(),
        "database": "wms_db"
    }

# TCP server status endpoint
@app.get("/tcp-status")
def tcp_server_status():
    """Get TCP server status and connected clients"""
    server = get_tcp_server()
    if server:
        return {
            "tcp_server": "running",
            "host": server.host,
            "port": server.port,
            "connected_clients": len(server.clients),
            "clients": server.get_connected_clients(),
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "tcp_server": "not_running",
            "timestamp": datetime.now().isoformat()
        }

# CRUD Operations

@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Validate status
    if not validate_status(order.status):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid options: received, in_warehouse, loaded, delivered"
        )
    
    # Check if order number already exists
    existing_order = db.query(Order).filter(Order.order_number == order.order_number).first()
    if existing_order:
        raise HTTPException(status_code=400, detail="Order number already exists")
    
    # Validate quantity
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Broadcast package received message via TCP
    if order.status == "received":
        package_data = {
            "package_id": f"PKG_{db_order.id}",
            "order_number": db_order.order_number,
            "customer_id": db_order.customer_id,
            "product_name": db_order.product_name,
            "quantity": db_order.quantity,
            "received_at": db_order.created_at.isoformat() + "Z",
            "warehouse_location": f"WH-{db_order.id % 10}-A"
        }
        await broadcast_package_received(package_data)
    
    return db_order

@app.get("/orders", response_model=List[OrderResponse])
def get_orders(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all orders with optional filters and pagination"""
    query = db.query(Order)
    
    if status:
        if not validate_status(status):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Valid options: received, in_warehouse, loaded, delivered"
            )
        query = query.filter(Order.status == status)
    
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    if driver_id:
        query = query.filter(Order.driver_id == driver_id)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/orders/number/{order_number}", response_model=OrderResponse)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """Get a specific order by order number"""
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Update an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate status if provided
    if order_update.status and not validate_status(order_update.status):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid options: received, in_warehouse, loaded, delivered"
        )
    
    # Check if new order number conflicts
    if order_update.order_number and order_update.order_number != order.order_number:
        existing = db.query(Order).filter(
            Order.order_number == order_update.order_number,
            Order.id != order_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Order number already exists")
    
    # Validate quantity if provided
    if order_update.quantity is not None and order_update.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    # Update fields
    update_data = order_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)
    
    db.commit()
    db.refresh(order)
    return order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Prevent deletion of delivered orders
    if order.status == "delivered":
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete delivered orders"
        )
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

# WMS-Specific Operations

@app.post("/warehouse/receive-order", response_model=OrderResponse)
def receive_order(order_data: OrderReceive, db: Session = Depends(get_db)):
    """Receive a new order into the warehouse"""
    # Check if order number already exists
    existing_order = db.query(Order).filter(Order.order_number == order_data.order_number).first()
    if existing_order:
        raise HTTPException(status_code=400, detail="Order already received")
    
    # Validate quantity
    if order_data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    db_order = Order(
        order_number=order_data.order_number,
        customer_id=order_data.customer_id,
        product_name=order_data.product_name,
        quantity=order_data.quantity,
        status="received"
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return db_order

@app.put("/warehouse/orders/{order_id}/assign-driver", response_model=OrderResponse)
async def assign_driver(order_id: int, assignment: DriverAssignment, db: Session = Depends(get_db)):
    """Assign a driver to an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate driver assignment based on order status
    if order.status not in ["received", "in_warehouse"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot assign driver to order with status: {order.status}"
        )
    
    old_status = order.status
    order.driver_id = assignment.driver_id
    
    # Auto-update status if order is ready
    order.status = "loaded"  # Always set to loaded when driver assigned
    
    db.commit()
    db.refresh(order)
    
    # Broadcast package loaded message via TCP
    package_data = {
        "package_id": f"PKG_{order.id}",
        "order_number": order.order_number,
        "customer_id": order.customer_id,
        "driver_id": order.driver_id,
        "vehicle_id": f"VEH_{order.driver_id}",
        "loaded_at": datetime.utcnow().isoformat() + "Z",
        "estimated_delivery": None  # Calculate based on route optimization
    }
    await broadcast_package_loaded(package_data)
    
    # Also broadcast status update
    status_data = {
        "package_id": f"PKG_{order.id}",
        "order_number": order.order_number,
        "old_status": old_status,
        "new_status": order.status,
        "driver_id": order.driver_id,
        "updated_by": "wms_system"
    }
    await broadcast_status_update(status_data)
    
    return order

@app.put("/warehouse/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)):
    """Update order status with warehouse workflow validation"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate status
    if not validate_status(status_update.status):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid options: received, in_warehouse, loaded, delivered"
        )
    
    # Validate status transition rules
    current_status = order.status
    new_status = status_update.status
    
    # Define valid transitions
    valid_transitions = {
        "received": ["in_warehouse"],
        "in_warehouse": ["loaded", "received"],  # Can go back to received if needed
        "loaded": ["delivered", "in_warehouse"],  # Can go back to warehouse if needed
        "delivered": []  # Final state, no transitions allowed
    }
    
    if new_status not in valid_transitions.get(current_status, []) and new_status != current_status:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status transition from '{current_status}' to '{new_status}'"
        )
    
    # Additional validation for loaded status
    if new_status == "loaded" and not order.driver_id:
        raise HTTPException(
            status_code=400, 
            detail="Cannot mark order as loaded without assigning a driver"
        )
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    return order

@app.get("/warehouse/orders/{order_id}/details", response_model=OrderResponse)
def get_order_details(order_id: int, db: Session = Depends(get_db)):
    """Get detailed information about an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/warehouse/orders/by-status/{status}", response_model=List[OrderResponse])
def get_orders_by_status(status: str, db: Session = Depends(get_db)):
    """Get all orders with a specific status"""
    if not validate_status(status):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid options: received, in_warehouse, loaded, delivered"
        )
    
    orders = db.query(Order).filter(Order.status == status).all()
    return orders

@app.get("/warehouse/orders/customer/{customer_id}", response_model=List[OrderResponse])
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    """Get all orders for a specific customer"""
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    if not orders:
        return []
    return orders

@app.get("/warehouse/orders/driver/{driver_id}", response_model=List[OrderResponse])
def get_driver_orders(driver_id: int, db: Session = Depends(get_db)):
    """Get all orders assigned to a specific driver"""
    orders = db.query(Order).filter(Order.driver_id == driver_id).all()
    if not orders:
        return []
    return orders

@app.get("/warehouse/dashboard")
def get_warehouse_dashboard(db: Session = Depends(get_db)):
    """Get warehouse dashboard statistics"""
    total_orders = db.query(Order).count()
    received_orders = db.query(Order).filter(Order.status == "received").count()
    in_warehouse_orders = db.query(Order).filter(Order.status == "in_warehouse").count()
    loaded_orders = db.query(Order).filter(Order.status == "loaded").count()
    delivered_orders = db.query(Order).filter(Order.status == "delivered").count()
    
    orders_with_drivers = db.query(Order).filter(Order.driver_id.isnot(None)).count()
    orders_without_drivers = db.query(Order).filter(Order.driver_id.is_(None)).count()
    
    return {
        "total_orders": total_orders,
        "status_breakdown": {
            "received": received_orders,
            "in_warehouse": in_warehouse_orders,
            "loaded": loaded_orders,
            "delivered": delivered_orders
        },
        "driver_assignment": {
            "assigned": orders_with_drivers,
            "unassigned": orders_without_drivers
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/warehouse/workflow-status")
def get_workflow_status(db: Session = Depends(get_db)):
    """Get current workflow status and bottlenecks"""
    received_count = db.query(Order).filter(Order.status == "received").count()
    in_warehouse_count = db.query(Order).filter(Order.status == "in_warehouse").count()
    loaded_count = db.query(Order).filter(Order.status == "loaded").count()
    
    # Identify bottlenecks
    bottlenecks = []
    if received_count > 10:
        bottlenecks.append("High number of received orders pending warehouse processing")
    if in_warehouse_count > 5:
        bottlenecks.append("Orders waiting for driver assignment")
    if loaded_count > 8:
        bottlenecks.append("Loaded orders pending delivery")
    
    return {
        "workflow_status": {
            "received_pending": received_count,
            "in_warehouse_pending": in_warehouse_count,
            "loaded_pending": loaded_count
        },
        "bottlenecks": bottlenecks if bottlenecks else ["No bottlenecks detected"],
        "recommendations": [
            "Process received orders to in_warehouse status",
            "Assign drivers to in_warehouse orders",
            "Coordinate delivery for loaded orders"
        ] if bottlenecks else ["Workflow operating smoothly"],
        "timestamp": datetime.now().isoformat()
    }

# Additional utility endpoints
@app.get("/warehouse/orders/recent", response_model=List[OrderResponse])
def get_recent_orders(limit: int = 10, db: Session = Depends(get_db)):
    """Get most recently created orders"""
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(limit).all()
    return orders

@app.get("/warehouse/orders/updated", response_model=List[OrderResponse])
def get_recently_updated_orders(limit: int = 10, db: Session = Depends(get_db)):
    """Get most recently updated orders"""
    orders = db.query(Order).order_by(Order.updated_at.desc()).limit(limit).all()
    return orders