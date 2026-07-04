from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
from datetime import datetime

def gen_id(): return uuid.uuid4().hex[:12]

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String(12), primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    subdomain = Column(String, unique=True, nullable=False)   # for multi‑shop hosting
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings = Column(Text, default="{}")  # JSON for shop name, address, etc.

class TaxRule(Base):
    __tablename__ = "tax_rules"
    id = Column(String(12), primary_key=True, default=gen_id)
    tenant_id = Column(String(12), ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)          # e.g., "GST", "PST", "HST"
    rate = Column(Float, nullable=False)           # 0.05 for 5%
    is_compound = Column(Boolean, default=False)   # if tax applies on top of another tax
    priority = Column(Integer, default=0)          # order of application
    is_default = Column(Boolean, default=True)
    tenant = relationship("Tenant")
