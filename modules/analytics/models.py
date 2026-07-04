from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from core.database import Base
import uuid

def gen_id(): return uuid.uuid4().hex[:12]

class ProductForecast(Base):
    __tablename__ = "product_forecasts"
    id = Column(String(12), primary_key=True, default=gen_id)
    product_id = Column(String(12), ForeignKey("products.id"), unique=True)
    
    # Velocity metrics (rolling averages)
    avg_daily_sales_7d = Column(Float, default=0.0)
    avg_daily_sales_30d = Column(Float, default=0.0)
    avg_daily_sales_90d = Column(Float, default=0.0)
    
    # AI Recommendations
    recommended_reorder_qty = Column(Integer, default=10)
    recommended_threshold = Column(Integer, default=5)
    
    last_calculated_at = Column(DateTime, nullable=True)
    product = relationship("Product")
