from modules.inventory.services import ProductService
from modules.customers.services import CustomerService
from modules.inventory.models import Product
from datetime import datetime
import json

class POSService:
    def __init__(self, db):
        self.db = db
        self.product_svc = ProductService(db)
        self.customer_svc = CustomerService(db) # to be created

    def calculate_totals(self, cart: list, tax_rates: list) -> dict:
        subtotal = round(sum(i["price"] * i["qty"] for i in cart), 2)
        tax_total = 0.0
        tax_lines = []
        for label, rate in tax_rates:
            amount = round(subtotal * rate, 2)
            tax_lines.append({"label": label, "amount": amount})
            tax_total += amount
        return {
            "subtotal": subtotal,
            "tax_lines": tax_lines,
            "tax_total": round(tax_total, 2),
            "total": round(subtotal + tax_total, 2),
        }

    def checkout(self, cart, customer_id, staff_id, payment_method, tendered):
        # ... full checkout logic moved from main.py
        pass
