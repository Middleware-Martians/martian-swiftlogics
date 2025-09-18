from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import time
import sys

# Database setup
DATABASE_URL = "postgresql://admin_user:admin_password@postgres:5432/cms_db"

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

# Order model
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    product_name = Column(String, index=True)
    quantity = Column(Integer)
    status = Column(String, default="pending")

# Create tables with retry logic
def create_tables_with_retry():
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully!")
            return
        except Exception as e:
            print(f"Table creation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries exceeded for table creation. Tables may need to be created manually.")
                # Don't exit, continue with the app

create_tables_with_retry()

# FastAPI app
app = FastAPI(title="CMS Service", description="Client Management System API")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "CMS"}

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schema
class OrderRequest(BaseModel):
    customer_id: int
    product_name: str
    quantity: int

# Create order
@app.post("/orders")
def create_order(order: OrderRequest, db: Session = Depends(get_db)):
    new_order = Order(
        customer_id=order.customer_id,
        product_name=order.product_name,
        quantity=order.quantity
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {"message": "Order created", "order": new_order.id}

# Get all orders
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders

# Get one order
@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Update order
@app.put("/orders/{order_id}")
def update_order(order_id: int, order: OrderRequest, db: Session = Depends(get_db)):
    existing = db.query(Order).filter(Order.id == order_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")
    existing.customer_id = order.customer_id
    existing.product_name = order.product_name
    existing.quantity = order.quantity
    db.commit()
    db.refresh(existing)
    return {"message": "Order updated", "order": existing.id}

# Delete order
@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": "Order deleted"}

# Get orders by customer_id (Customer view)
@app.get("/customers/{customer_id}/orders")
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    if not orders:
        return {"message": f"No orders found for customer {customer_id}", "orders": []}
    return {
        "customer_id": customer_id,
        "total_orders": len(orders),
        "orders": orders
    }