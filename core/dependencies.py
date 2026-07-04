from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.tenant import get_tenant
from modules.tenants.models import Tenant

def get_current_tenant(request: Request, db: Session = Depends(get_db)) -> Tenant:
    return get_tenant(request, db)
