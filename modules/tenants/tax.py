from sqlalchemy.orm import Session
from modules.tenants.models import TaxRule, Tenant
from typing import List, Dict

class TaxService:
    def __init__(self, db: Session, tenant: Tenant):
        self.db = db
        self.tenant = tenant

    def get_tax_rules(self) -> List[TaxRule]:
        return self.db.query(TaxRule).filter(TaxRule.tenant_id == self.tenant.id).order_by(TaxRule.priority).all()

    def calculate_tax(self, taxable: float) -> Dict:
        rules = self.get_tax_rules()
        lines = []
        tax_total = 0.0
        for rule in rules:
            # If compound, rate applies on the current subtotal including previous taxes
            base = taxable + tax_total if rule.is_compound else taxable
            amount = round(base * rule.rate, 2)
            lines.append({
                "label": f"{rule.name} ({rule.rate*100:.3g}%)",
                "amount": amount
            })
            tax_total += amount
        return {"lines": lines, "tax_total": round(tax_total, 2), "total": round(taxable + tax_total, 2)}
