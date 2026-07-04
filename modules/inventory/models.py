from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

def gen_id():
    return uuid.uuid4().hex[:12]

class Category(Base):
    __tablename__ = "categories"
    id = Column(String(12), primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    parent_id = Column(String(12), ForeignKey("categories.id"), nullable=True)
    products = relationship("Product", back_populates="category")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(String(12), primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    contact_name = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    payment_terms = Column(String, default="NET30")
    balance = Column(Float, default=0.0)
    products = relationship("Product", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"
    id = Column(String(12), primary_key=True, default=gen_id)
    sku = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    category_id = Column(String(12), ForeignKey("categories.id"))
    supplier_id = Column(String(12), ForeignKey("suppliers.id"))
    price = Column(Float, default=0)
    cost = Column(Float, default=0)
    stock = Column(Integer, default=0)
    reserved_stock = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=5)
    reorder_qty = Column(Integer, default=10)
    location = Column(String, default="Main Shelf")
    last_movement_at = Column(DateTime, nullable=True)
    
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    movements = relationship("StockMovement", back_populates="product")

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(String(12), primary_key=True, default=gen_id)
    product_id = Column(String(12), ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    type = Column(String, nullable=False) # SALE, RESTOCK, ADJUST, RETURN
    reference_id = Column(String(12), nullable=True)
    created_at = Column(DateTime, server_default=sqlalchemy.func.now())
    product = relationship("Product", back_populates="movements")
