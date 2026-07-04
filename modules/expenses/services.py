from sqlalchemy.orm import Session
from modules.expenses.models import Expense  # Already defined in previous migration
from modules.auth.models import Staff
import uuid

def gen_id():
    return uuid.uuid4().hex[:12]

class ExpenseService:
    def __init__(self, db: Session):
        self.db = db

    def add_expense(self, description: str, amount: float, category: str, staff_id: str = None):
        expense = Expense(
            id=gen_id(),
            description=description,
            amount=amount,
            category=category,
            staff_id=staff_id
        )
        self.db.add(expense)
        self.db.commit()
        return expense

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def get_employees(self):
        return self.db.query(Staff).filter(Staff.active == True).all()  # noqa: E712

    def add_employee(self, name: str, role: str, pin_hash: str):
        staff = Staff(id=gen_id(), name=name, role=role, pin_hash=pin_hash, active=True)
        self.db.add(staff)
        self.db.commit()
        return staff
