from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import os

from core.database import get_db, engine
from core.config import settings
from modules.inventory.services import ProductService
from modules.pos.services import POSService
from modules.repairs.services import RepairService
from modules.auth.services import AuthService
from auth import get_current_staff, role_allowed

app = FastAPI(title="TechPro+ CRM V2")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff: return RedirectResponse("/login")
    # Service calls to gather analytics...
    return templates.TemplateResponse("dashboard.html", {"staff": staff, "sales_today": 0, "repairs_today": 0, ...})

@app.get("/pos")
def pos(request: Request, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff: return RedirectResponse("/login")
    products = db.query(Product).all()
    cart = request.session.get("cart", [])
    # Calculate taxes...
    return templates.TemplateResponse("pos.html", {"staff": staff, "products": products, "cart": cart, "subtotal": 0, "tax": 0, "total": 0})

@app.post("/pos/scan")
async def pos_scan(request: Request, sku: str = Form(...), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.sku == sku).first()
    cart = request.session.get("cart", [])
    if product:
        cart.append({"id": product.id, "name": product.name, "price": product.price, "qty": 1})
        request.session["cart"] = cart
    return RedirectResponse("/pos", status_code=303)

@app.get("/repairs")
def repairs(request: Request, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff: return RedirectResponse("/login")
    repairs = db.query(Repair).all()
    columns = {s: [] for s in ['RECEIVED', 'DIAGNOSING', 'WAITING', 'REPAIRING', 'READY']}
    for r in repairs:
        if r.status in columns: columns[r.status].append(r)
    return templates.TemplateResponse("repairs.html", {"staff": staff, "columns": columns})

@app.post("/repairs/add")
def add_repair(request: Request, name: str = Form(...), phone: str = Form(...), brand: str = Form(""), model: str = Form(""), description: str = Form(""), db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    # Logic to create customer and repair ticket...
    return RedirectResponse("/repairs", status_code=303)

@app.get("/login")
def login_page(request: Request): return templates.TemplateResponse("login.html", {"error": None})

from modules.purchasing.services import PurchaseOrderService
from modules.expenses.services import ExpenseService, EmployeeService

# --- SUPPLIERS ---
@app.get("/suppliers")
def suppliers_page(request: Request, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff or not role_allowed(staff, "owner", "manager"): return RedirectResponse("/login")
    suppliers = db.query(Supplier).all()
    return templates.TemplateResponse("suppliers.html", {"staff": staff, "suppliers": suppliers})

@app.post("/suppliers/add")
def supplier_add(request: Request, name: str = Form(...), contact_name: str = Form(""), phone: str = Form(""), email: str = Form(""), payment_terms: str = Form("NET30"), db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff or not role_allowed(staff, "owner", "manager"): return RedirectResponse("/login")
    supplier = Supplier(id=gen_id(), name=name, contact_name=contact_name, phone=phone, email=email, payment_terms=payment_terms)
    db.add(supplier)
    db.commit()
    return RedirectResponse("/suppliers", status_code=303)

# --- PURCHASE ORDERS ---
@app.get("/purchase-orders")
def pos_page(request: Request, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff or not role_allowed(staff, "owner", "manager"): return RedirectResponse("/login")
    pos = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).all()
    suppliers = db.query(Supplier).all()
    products = db.query(Product).all()
    return templates.TemplateResponse("purchase_orders.html", {"staff": staff, "purchase_orders": pos, "suppliers": suppliers, "products": products})

@app.post("/purchase-orders/add")
def po_add(request: Request, supplier_id: str = Form(...), product_id: list = Form(...), qty: list = Form(...), unit_price: list = Form(...), db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff or not role_allowed(staff, "owner", "manager"): return RedirectResponse("/login")
    service = PurchaseOrderService(db)
    items = [{"product_id": pid, "qty": int(q), "unit_price": float(p)} for pid, q, p in zip(product_id, qty, unit_price)]
    service.create_po(supplier_id, items)
    return RedirectResponse("/purchase-orders", status_code=303)

@app.post("/purchase-orders/{po_id}/send")
def po_send(request: Request, po_id: str, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff or not role_allowed(staff, "owner", "manager"): return RedirectResponse("/login")
    PurchaseOrderService(db).send_po(po_id)
    return RedirectResponse("/purchase-orders", status_code=303)

@app.post("/purchase-orders/{po_id}/receive")
def po_receive(request: Request, po_id: str, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff or not role_allowed(staff, "owner", "manager"): return RedirectResponse("/login")
    po = PurchaseOrderService(db).receive_po(po_id)
    if not po:
        return HTMLResponse("PO not found or already received.", status_code=400)
    return RedirectResponse("/purchase-orders", status_code=303)

# --- EXPENSES ---
@app.get("/expenses")
def expenses_page(request: Request, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff or not role_allowed(staff, "owner", "manager"): return RedirectResponse("/login")
    expenses = db.query(Expense).order_by(Expense.date.desc()).all()
    return templates.TemplateResponse("expenses.html", {"staff": staff, "expenses": expenses})

@app.post("/expenses/add")
def expense_add(request: Request, description: str = Form(...), amount: float = Form(...), category: str = Form(...), db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff: return RedirectResponse("/login")
    ExpenseService(db).add_expense(description, amount, category, staff.id if staff else None)
    return RedirectResponse("/expenses", status_code=303)

# --- EMPLOYEES (Staff Management) ---
@app.get("/employees")
def employees_page(request: Request, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff or not role_allowed(staff, "owner", "manager"): return RedirectResponse("/login")
    employees = db.query(Staff).all()
    return templates.TemplateResponse("staff.html", {"staff": staff, "all_staff": employees})
from modules.warranty.services import WarrantyService
from modules.warranty.models import Warranty

@app.get("/warranties")
def warranties_page(request: Request, db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff: return RedirectResponse("/login")
    
    warranties = db.query(Warranty).order_by(Warranty.end_date).all()
    return templates.TemplateResponse("warranties.html", {"staff": staff, "warranties": warranties})

@app.post("/repairs/{repair_id}/warranty/add")
def add_repair_warranty(request: Request, repair_id: str, duration_days: int = Form(90), db: Session = Depends(get_db)):
    staff = get_current_staff(request, db)
    if not staff: return RedirectResponse("/login")
    
    from modules.repairs.models import Repair
    repair = db.get(Repair, repair_id)
    if not repair or not repair.customer_id:
        return HTMLResponse("Repair not found or missing customer.", status_code=400)
    
    WarrantyService(db).create_repair_warranty(repair.customer_id, repair_id, duration_days)
    return RedirectResponse(f"/warranties", status_code=303)
from core.dependencies import get_current_tenant
from modules.tenants.models import Tenant

@app.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    staff: Staff = Depends(require_permission("dashboard"))
):
    # Now use tenant to filter everything
    products = db.query(Product).filter(Product.tenant_id == tenant.id).all()
    return templates.TemplateResponse("dashboard.html", {...})
@app.post("/settings/tax")
def save_tax_rules(
    request: Request,
    name: List[str] = Form(...),
    rate: List[float] = Form(...),
    compound: List[str] = Form([]),  # only checked boxes send their value
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    staff: Staff = Depends(require_permission("settings"))
):
    # Delete existing rules for this tenant
    db.query(TaxRule).filter(TaxRule.tenant_id == tenant.id).delete()
    # Insert new ones
    for i, n in enumerate(name):
        rule = TaxRule(
            tenant_id=tenant.id,
            name=n,
            rate=rate[i],
            is_compound=(compound[i] == 'on') if i < len(compound) else False,
            priority=i
        )
        db.add(rule)
    db.commit()
    return RedirectResponse("/settings", status_code=303)
