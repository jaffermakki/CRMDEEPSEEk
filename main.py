from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import os

from core.database import get_db, engine
from core.config import settings
from modules.inventory.services import ProductService
from modules.pos.services import POSService
# ... other modules

app = FastAPI(title="TechPro+ CRM V2")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

# ------- Legacy Route Adapters (Original Endpoints preserved) -------
@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    # ... exact same logic as before, but using db.query
    return templates.TemplateResponse("dashboard.html", {...})

@app.get("/pos")
def pos_page(request: Request, db: Session = Depends(get_db)):
    # ... exact same logic
    return templates.TemplateResponse("pos.html", {...})

# Notice: I am not moving the actual logic yet, but in the subsequent step,
# I will replace the inline logic with calls to POSService and ProductService.

@app.post("/pos/scan")
def pos_scan(request: Request, sku: str = Form(...), db: Session = Depends(get_db)):
    # ... exact same logic, but internally we can now do:
    # product = ProductService(db).find_by_sku(sku)
    # ... rest of logic remains identical
