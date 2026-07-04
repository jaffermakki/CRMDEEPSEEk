# Permission Matrix
# Format: {'role': {'module': [actions]}}
PERMISSIONS = {
    'owner': {
        '*': ['read', 'write', 'delete', 'manage']  # Full access
    },
    'manager': {
        'dashboard': ['read'],
        'pos': ['read', 'write'],
        'repairs': ['read', 'write'],
        'inventory': ['read', 'write'],
        'customers': ['read', 'write'],
        'reports': ['read'],
        'suppliers': ['read', 'write'],
        'purchase_orders': ['read', 'write'],
        'expenses': ['read', 'write'],
        'staff': ['read'],  # Can see staff, but not add/edit
        'settings': [],     # No access
        'warranties': ['read', 'write'],
    },
    'technician': {
        'dashboard': ['read'],
        'repairs': ['read', 'write'],
        'inventory': ['read'],
        'customers': ['read'],
    },
    'cashier': {
        'dashboard': ['read'],
        'pos': ['read', 'write'],
        'inventory': ['read'],
        'customers': ['read', 'write'],
        'repairs': ['read'],  # Can see but not modify
    }
}

def has_permission(staff, module: str, action: str = 'read') -> bool:
    if not staff or not staff.active:
        return False
    role_perms = PERMISSIONS.get(staff.role, {})
    if '*' in role_perms and action in role_perms['*']:
        return True
    if module not in role_perms:
        return False
    return action in role_perms[module]
