from core.database import SessionLocal, Base, engine
from modules.inventory.models import Category, Product, Supplier
from modules.auth.models import Staff
from auth import hash_pin
import random

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 1. Staff
owner = Staff(id="s1", name="Owner", role="owner", pin_hash=hash_pin("1234"), active=True)
tech = Staff(id="s2", name="John Tech", role="technician", pin_hash=hash_pin("5678"), active=True)
db.add_all([owner, tech])

# 2. Categories
cat_parts = Category(id="c1", name="Spare Parts")
cat_acc = Category(id="c2", name="Accessories")
db.add_all([cat_parts, cat_acc])

# 3. Suppliers
supp = Supplier(id="sup1", name="Mobile Parts Inc", contact_name="Mike", phone="555-0100", email="mike@parts.com")
db.add(supp)

# 4. Products
products = [
    Product(id="p1", sku="BATT-IP13", name="iPhone 13 Battery", category=cat_parts, supplier=supp, price=49.99, cost=18.00, stock=25, reorder_threshold=5, reorder_qty=10),
    Product(id="p2", sku="SCRN-IP13", name="iPhone 13 Screen", category=cat_parts, supplier=supp, price=149.99, cost=55.00, stock=8, reorder_threshold=5, reorder_qty=5),
    Product(id="p3", sku="CASE-OTTER", name="OtterBox Case - iPhone", category=cat_acc, supplier=supp, price=29.99, cost=8.00, stock=40, reorder_threshold=10),
]
db.add_all(products)

# 5. Customers
from modules.customers.models import Customer
c1 = Customer(id="c1", name="Alice Wong", phone="555-1234", email="alice@email.com")
db.add(c1)

db.commit()
print("✅ Fresh database seeded with demo data.")

# Add this to the end of your seed.py
from modules.warranty.models import Warranty, WarrantyType
from datetime import date, timedelta

# ... existing seed code ...

# Create a product warranty expiring in 6 days (to trigger automation)
future_warranty = Warranty(
    id="w1",
    reference_type=WarrantyType.PRODUCT,
    reference_id="p1",
    customer_id="c1",
    start_date=date.today() - timedelta(days=359),
    end_date=date.today() + timedelta(days=6) # Expires in 6 days
)
db.add(future_warranty)
db.commit()
