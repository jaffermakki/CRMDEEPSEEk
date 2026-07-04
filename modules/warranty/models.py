from sqlalchemy import Column, String, Date, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
import enum

def gen_id():
    return uuid.uuid4().hex[:12]

class WarrantyType(str, enum.Enum):
    PRODUCT = "product"
    REPAIR = "repair"

class WarrantyStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"

class Warranty(Base):
    __tablename__ = "warranties"
    id = Column(String(12), primary_key=True, default=gen_id)
    reference_type = Column(Enum(WarrantyType), nullable=False)
    reference_id = Column(String(12), nullable=False)  # FK to Product.id or Repair.id
    customer_id = Column(String(12), ForeignKey("customers.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(WarrantyStatus), default=WarrantyStatus.ACTIVE)
    notes = Column(Text, default="")
    
    customer = relationship("Customer")
