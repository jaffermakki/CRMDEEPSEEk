from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

def gen_id(): return uuid.uuid4().hex[:12]

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(String(12), primary_key=True, default=gen_id)
    po_number = Column(String, unique=True, nullable=False)
    supplier_id = Column(String(12), ForeignKey("suppliers.id"))
    status = Column(Enum("DRAFT", "SENT", "RECEIVED", "CANCELLED", name="po_status"), default="DRAFT")
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=sqlalchemy.func.now())
    received_at = Column(DateTime, nullable=True)
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")

class PurchaseOrderItem(Base):
    __tablename__ = "po_items"
    id = Column(String(12), primary_key=True, default=gen_id)
    po_id = Column(String(12), ForeignKey("purchase_orders.id"))
    product_id = Column(String(12), ForeignKey("products.id"))
    qty = Column(Integer)
    unit_price = Column(Float)
    received_qty = Column(Integer, default=0)
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
