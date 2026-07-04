from fastapi import Request
from sqlalchemy.orm import Session
from modules.tenants.models import Tenant

async def get_tenant(request: Request, db: Session) -> Tenant:
    # 1. Try to extract from subdomain (e.g., 'shop1.localhost')
    host = request.headers.get("host", "")
    subdomain = host.split('.')[0] if '.' in host else None
    if subdomain and subdomain not in ('www', 'api'):
        tenant = db.query(Tenant).filter(Tenant.subdomain == subdomain, Tenant.active == True).first()
        if tenant:
            return tenant
    # 2. Fallback: default tenant (for local development)
    return db.query(Tenant).filter(Tenant.subdomain == 'default').first()
