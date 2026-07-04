"""add tenant and tax rules

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-04

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. Create tenant table
    op.create_table('tenants',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('subdomain', sa.String(), unique=True, nullable=False),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('settings', sa.Text(), default='{}'),
    )

    # 2. Add a default tenant (for existing single‑shop setups)
    op.execute("INSERT INTO tenants (id, name, subdomain, active, settings) VALUES ('t1', 'Default Shop', 'default', 1, '{}')")

    # 3. Create tax rules table
    op.create_table('tax_rules',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('tenant_id', sa.String(12), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('rate', sa.Float(), nullable=False),
        sa.Column('is_compound', sa.Boolean(), default=False),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('is_default', sa.Boolean(), default=True),
    )

    # 4. Add default tax rules (e.g., HST 13% for Ontario)
    op.execute("INSERT INTO tax_rules (id, tenant_id, name, rate, is_compound, priority, is_default) VALUES ('tr1', 't1', 'HST', 0.13, 0, 0, 1)")

    # 5. Add tenant_id to all existing tables that need isolation
    tables = ['products', 'customers', 'repairs', 'invoices', 'invoice_lines', 'held_carts', 
              'cash_sessions', 'purchase_orders', 'stock_movements', 'expenses', 'warranties', 
              'staff', 'settings']
    for table in tables:
        with op.batch_alter_table(table) as batch_op:
            batch_op.add_column(sa.Column('tenant_id', sa.String(12), sa.ForeignKey('tenants.id'), nullable=True))
            # For existing rows, set tenant_id to the default tenant
            batch_op.execute(f"UPDATE {table} SET tenant_id = 't1'")

    # 6. Now make tenant_id NOT NULL
    for table in tables:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column('tenant_id', nullable=False)

def downgrade():
    # Drop tenant_id columns
    tables = ['products', 'customers', 'repairs', 'invoices', 'invoice_lines', 'held_carts', 
              'cash_sessions', 'purchase_orders', 'stock_movements', 'expenses', 'warranties', 
              'staff', 'settings']
    for table in tables:
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_column('tenant_id')
    op.drop_table('tax_rules')
    op.drop_table('tenants')
