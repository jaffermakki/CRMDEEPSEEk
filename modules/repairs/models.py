from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

def gen_id(): return uuid.uuid4().hex[:12]

class Repair(Base):
    __tablename__ = "repairs"
    id = Column(String(12), primary_key=True, default=gen_id)
    ticket_no = Column(Integer, default=1001)
    customer_id = Column(String(12), ForeignKey("customers.id"))
    device = Column(String)
    brand = Column(String)
    model = Column(String)
    imei_1 = Column(String)
    imei_2 = Column(String)
    serial_number = Column(String)
    storage = Column(String)
    color = Column(String)
    passcode = Column(String)
    water_damage = Column(Boolean, default=False)
    accessories_received = Column(Text, default="[]") # JSON array
    issue = Column(String)
    description = Column(Text)
    status = Column(String, default="RECEIVED")
    estimated_cost = Column(Float)
    final_cost = Column(Float)
    warranty_days = Column(Integer, default=90)
    promised_by = Column(String)
    technician_id = Column(String(12), ForeignKey("staff.id"))
    status_history = Column(Text, default="[]")
    created_at = Column(DateTime, server_default=sqlalchemy.func.now())
    updated_at = Column(DateTime, onupdate=sqlalchemy.func.now())
    
    customer = relationship("Customer")
    technician = relationship("Staff")
    parts_used = relationship("RepairPart", back_populates="repair")

class RepairPart(Base):
    __tablename__ = "repair_parts"
    id = Column(String(12), primary_key=True, default=gen_id)
    repair_id = Column(String(12), ForeignKey("repairs.id"))
    product_id = Column(String(12), ForeignKey("products.id"))
    qty = Column(Integer, default=1)
    price = Column(Float)
    repair = relationship("Repair", back_populates="parts_used")
    product = relationship("Product")
