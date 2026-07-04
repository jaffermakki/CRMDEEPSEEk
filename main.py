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
