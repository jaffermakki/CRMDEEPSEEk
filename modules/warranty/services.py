from sqlalchemy.orm import Session
from modules.warranty.models import Warranty, WarrantyType, WarrantyStatus
from datetime import date, timedelta
import uuid

def gen_id(): return uuid.uuid4().hex[:12]

class WarrantyService:
    def __init__(self, db: Session):
        self.db = db

    def create_product_warranty(self, customer_id: str, product_id: str, duration_days: int = 365) -> Warranty:
        start = date.today()
        end = start + timedelta(days=duration_days)
        warranty = Warranty(
            id=gen_id(),
            reference_type=WarrantyType.PRODUCT,
            reference_id=product_id,
            customer_id=customer_id,
            start_date=start,
            end_date=end
        )
        self.db.add(warranty)
        self.db.commit()
        return warranty

    def create_repair_warranty(self, customer_id: str, repair_id: str, duration_days: int = 90) -> Warranty:
        start = date.today()
        end = start + timedelta(days=duration_days)
        warranty = Warranty(
            id=gen_id(),
            reference_type=WarrantyType.REPAIR,
            reference_id=repair_id,
            customer_id=customer_id,
            start_date=start,
            end_date=end
        )
        self.db.add(warranty)
        self.db.commit()
        return warranty
