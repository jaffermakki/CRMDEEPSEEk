from core.repository import BaseRepository
from modules.inventory.models import Product, ProductCategory, Supplier
from sqlalchemy.orm import Session
from typing import List, Optional

class ProductService:
    def __init__(self, db: Session):
        self.repo = BaseRepository(Product, db)
        self.db = db

    def get_product(self, product_id: str) -> Optional[Product]:
        return self.repo.get(product_id)

    def get_low_stock(self) -> List[Product]:
        return self.db.query(Product).filter(Product.stock <= Product.reorder_threshold).all()

    def create_product(self, sku: str, name: str, price: float, cost: float, stock: int) -> Product:
        # Legacy support: this still works with old fields
        product = Product(sku=sku, name=name, price=price, cost=cost, stock=stock)
        self.repo.add(product)
        self.db.commit()
        return product
