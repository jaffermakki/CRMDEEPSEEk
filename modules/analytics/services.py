from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, timezone
from modules.inventory.models import Product
from modules.pos.models import InvoiceLine  # Assuming invoice lines link to products
from modules.analytics.models import ProductForecast
import math

class ForecastingService:
    def __init__(self, db: Session):
        self.db = db

    def update_forecast_for_product(self, product_id: str):
        now = datetime.now(timezone.utc)
        intervals = {
            '7d': (now - timedelta(days=7)),
            '30d': (now - timedelta(days=30)),
            '90d': (now - timedelta(days=90))
        }
        
        sales_data = {}
        for key, start_date in intervals.items():
            total_qty = self.db.query(func.sum(InvoiceLine.qty)).filter(
                InvoiceLine.product_id == product_id,
                InvoiceLine.invoice.has(date >= start_date)
            ).scalar() or 0
            
            days = 7 if key == '7d' else 30 if key == '30d' else 90
            avg = total_qty / days
            sales_data[key] = avg

        # Find existing forecast or create new
        forecast = self.db.query(ProductForecast).filter(
            ProductForecast.product_id == product_id
        ).first()
        if not forecast:
            forecast = ProductForecast(product_id=product_id)
            self.db.add(forecast)

        forecast.avg_daily_sales_7d = sales_data['7d']
        forecast.avg_daily_sales_30d = sales_data['30d']
        forecast.avg_daily_sales_90d = sales_data['90d']
        
        # AI Logic: Use 30-day velocity to calculate reorder_qty
        # Safe stock = avg daily sales * lead time (assume 5 days) * safety buffer (1.5)
        # Reorder qty = Safe stock * 2
        lead_time_days = 5
        daily_velocity = forecast.avg_daily_sales_30d if forecast.avg_daily_sales_30d > 0 else 1
        safe_stock = math.ceil(daily_velocity * lead_time_days * 1.5)
        
        forecast.recommended_reorder_qty = max(10, safe_stock * 2)
        forecast.recommended_threshold = max(5, math.ceil(safe_stock))
        forecast.last_calculated_at = now
        
        self.db.commit()
        return forecast
