from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List, Optional
import time
import sys
import math
import asyncio
from datetime import datetime

# Database setup
DATABASE_URL = "postgresql://admin_user:admin_password@postgres:5432/ros_db"

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

# Database Models
class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    vehicle_number = Column(String, unique=True, index=True)
    contact_number = Column(String)
    current_location_lat = Column(Float)
    current_location_long = Column(Float)
    
    # Relationship with orders
    orders = relationship("Order", back_populates="driver")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    product_name = Column(String, index=True)
    quantity = Column(Integer)
    address = Column(String)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    status = Column(String, default="pending")
    
    # Relationship with driver
    driver = relationship("Driver", back_populates="orders")

# Pydantic Models
class DriverCreate(BaseModel):
    name: str
    vehicle_number: str
    contact_number: str
    current_location_lat: float
    current_location_long: float

class DriverResponse(BaseModel):
    id: int
    name: str
    vehicle_number: str
    contact_number: str
    current_location_lat: float
    current_location_long: float
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: int
    product_name: str
    quantity: int
    address: str
    driver_id: Optional[int] = None

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    product_name: str
    quantity: int
    address: str
    driver_id: Optional[int]
    status: str
    
    class Config:
        from_attributes = True

class RouteOptimizationRequest(BaseModel):
    order_ids: List[int]
    available_driver_ids: List[int]

class OptimizedRoute(BaseModel):
    driver_id: int
    driver_name: str
    assigned_orders: List[OrderResponse]
    total_distance: float
    estimated_time: float

class RouteOptimizationResponse(BaseModel):
    optimized_routes: List[OptimizedRoute]
    total_orders_assigned: int
    unassigned_orders: List[OrderResponse]

# Create tables with retry logic
def create_tables_with_retry():
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("ROS Tables created successfully!")
            return
        except Exception as e:
            print(f"Table creation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries exceeded for table creation. Tables may need to be created manually.")

create_tables_with_retry()

# FastAPI app
app = FastAPI(
    title="ROS Service", 
    description="Route Optimization System API for SwiftLogistics",
    version="1.0.0"
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions for route optimization
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def get_coordinates_from_address(address: str) -> tuple:
    """Simple mapping of addresses to coordinates for demonstration"""
    city_coordinates = {
        "colombo": (6.9271, 79.8612),
        "kandy": (7.2906, 80.6337),
        "galle": (6.0535, 80.2210),
        "jaffna": (9.6615, 80.0255),
        "anuradhapura": (8.3114, 80.4037),
        "batticaloa": (7.7102, 81.6924),
        "ratnapura": (6.6828, 80.3992),
        "kurunegala": (7.4818, 80.3653),
        "badulla": (6.9934, 81.0550),
        "matara": (5.9549, 80.5550)
    }
    
    # Simple address matching (case insensitive)
    for city, coords in city_coordinates.items():
        if city.lower() in address.lower():
            return coords
    
    # Default coordinates if no match (Colombo)
    return (6.9271, 79.8612)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ROS", "timestamp": datetime.now().isoformat()}

# Driver CRUD Operations
@app.post("/drivers", response_model=DriverResponse)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    """Create a new driver"""
    # Check if vehicle number already exists
    existing_driver = db.query(Driver).filter(Driver.vehicle_number == driver.vehicle_number).first()
    if existing_driver:
        raise HTTPException(status_code=400, detail="Vehicle number already registered")
    
    db_driver = Driver(**driver.dict())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

@app.get("/drivers", response_model=List[DriverResponse])
def get_drivers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all drivers with pagination"""
    drivers = db.query(Driver).offset(skip).limit(limit).all()
    return drivers

@app.get("/drivers/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    """Get a specific driver by ID"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@app.put("/drivers/{driver_id}", response_model=DriverResponse)
def update_driver(driver_id: int, driver_update: DriverCreate, db: Session = Depends(get_db)):
    """Update a driver's information"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Check if new vehicle number conflicts with existing ones
    if driver_update.vehicle_number != driver.vehicle_number:
        existing = db.query(Driver).filter(
            Driver.vehicle_number == driver_update.vehicle_number,
            Driver.id != driver_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Vehicle number already registered")
    
    for key, value in driver_update.dict().items():
        setattr(driver, key, value)
    
    db.commit()
    db.refresh(driver)
    return driver

@app.delete("/drivers/{driver_id}")
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    """Delete a driver"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Check if driver has active orders
    active_orders = db.query(Order).filter(
        Order.driver_id == driver_id,
        Order.status.in_(["pending", "assigned", "in_transit"])
    ).count()
    
    if active_orders > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete driver with {active_orders} active orders"
        )
    
    db.delete(driver)
    db.commit()
    return {"message": "Driver deleted successfully"}

# Order CRUD Operations
@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Validate driver if provided
    if order.driver_id:
        driver = db.query(Driver).filter(Driver.id == order.driver_id).first()
        if not driver:
            raise HTTPException(status_code=400, detail="Invalid driver ID")
    
    db_order = Order(**order.dict())
    if order.driver_id:
        db_order.status = "assigned"
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders", response_model=List[OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all orders with optional status filter and pagination"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_update: OrderCreate, db: Session = Depends(get_db)):
    """Update an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate driver if provided
    if order_update.driver_id:
        driver = db.query(Driver).filter(Driver.id == order_update.driver_id).first()
        if not driver:
            raise HTTPException(status_code=400, detail="Invalid driver ID")
    
    for key, value in order_update.dict().items():
        setattr(order, key, value)
    
    # Update status based on driver assignment
    if order.driver_id and order.status == "pending":
        order.status = "assigned"
    elif not order.driver_id and order.status == "assigned":
        order.status = "pending"
    
    db.commit()
    db.refresh(order)
    return order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status in ["in_transit", "delivered"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete order with status: {order.status}"
        )
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

# Route Optimization Endpoint
@app.post("/optimize-routes", response_model=RouteOptimizationResponse)
def optimize_routes(request: RouteOptimizationRequest, db: Session = Depends(get_db)):
    """Optimize routes by assigning orders to drivers"""
    
    # Get orders and drivers
    orders = db.query(Order).filter(Order.id.in_(request.order_ids)).all()
    drivers = db.query(Driver).filter(Driver.id.in_(request.available_driver_ids)).all()
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    if not drivers:
        raise HTTPException(status_code=404, detail="No drivers found")
    
    # Simple route optimization algorithm
    optimized_routes = []
    unassigned_orders = []
    orders_per_driver = len(orders) // len(drivers) + 1
    
    for i, driver in enumerate(drivers):
        driver_orders = orders[i * orders_per_driver:(i + 1) * orders_per_driver]
        
        if not driver_orders:
            continue
        
        # Calculate total distance for this driver's route
        total_distance = 0.0
        current_lat, current_lon = driver.current_location_lat, driver.current_location_long
        
        for order in driver_orders:
            order_lat, order_lon = get_coordinates_from_address(order.address)
            distance = calculate_distance(current_lat, current_lon, order_lat, order_lon)
            total_distance += distance
            current_lat, current_lon = order_lat, order_lon
            
            # Update order status and assignment
            order.driver_id = driver.id
            order.status = "assigned"
        
        # Estimated time (assuming 50 km/h average speed)
        estimated_time = total_distance / 50.0
        
        optimized_route = OptimizedRoute(
            driver_id=driver.id,
            driver_name=driver.name,
            assigned_orders=[OrderResponse.from_orm(order) for order in driver_orders],
            total_distance=round(total_distance, 2),
            estimated_time=round(estimated_time, 2)
        )
        optimized_routes.append(optimized_route)
    
    # Handle remaining unassigned orders
    assigned_count = sum(len(route.assigned_orders) for route in optimized_routes)
    if assigned_count < len(orders):
        unassigned_orders = [
            OrderResponse.from_orm(order) 
            for order in orders[assigned_count:]
        ]
    
    # Commit the changes to database
    db.commit()
    
    return RouteOptimizationResponse(
        optimized_routes=optimized_routes,
        total_orders_assigned=assigned_count,
        unassigned_orders=unassigned_orders
    )

# Additional utility endpoints
@app.get("/drivers/{driver_id}/orders", response_model=List[OrderResponse])
def get_driver_orders(driver_id: int, db: Session = Depends(get_db)):
    """Get all orders assigned to a specific driver"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    orders = db.query(Order).filter(Order.driver_id == driver_id).all()
    return orders

@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    """Update order status"""
    valid_statuses = ["pending", "assigned", "in_transit", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid options: {', '.join(valid_statuses)}"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    db.refresh(order)
    
    return {"message": f"Order status updated to {status}", "order_id": order_id}

@app.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_drivers = db.query(Driver).count()
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    assigned_orders = db.query(Order).filter(Order.status == "assigned").count()
    in_transit_orders = db.query(Order).filter(Order.status == "in_transit").count()
    delivered_orders = db.query(Order).filter(Order.status == "delivered").count()
    
    return {
        "total_drivers": total_drivers,
        "total_orders": total_orders,
        "order_status_breakdown": {
            "pending": pending_orders,
            "assigned": assigned_orders,
            "in_transit": in_transit_orders,
            "delivered": delivered_orders
        },
        "timestamp": datetime.now().isoformat()
    }