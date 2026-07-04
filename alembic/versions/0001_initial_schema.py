"""initial schema v2

Revision ID: 0001
Revises: 
Create Date: 2026-07-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import TEXT

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create new normalized tables
    op.create_table('product_categories',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('parent_id', sa.String(12), nullable=True),
    )
    
    op.create_table('suppliers',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_name', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('payment_terms', sa.String(), default='NET30'),
        sa.Column('balance', sa.Float(), default=0.0),
    )

    op.create_table('purchase_orders',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('po_number', sa.String(), unique=True, nullable=False),
        sa.Column('supplier_id', sa.String(12), sa.ForeignKey('suppliers.id')),
        sa.Column('status', sa.String(), default='DRAFT'),
        sa.Column('total', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('received_at', sa.DateTime(), nullable=True),
    )

    op.create_table('product_movements',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('product_id', sa.String(12), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False), # SALE, RESTOCK, ADJUST, RETURN
        sa.Column('reference_id', sa.String(12), nullable=True), # Invoice ID or PO ID
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('repair_parts_used',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('repair_id', sa.String(12), sa.ForeignKey('repairs.id'), nullable=False),
        sa.Column('product_id', sa.String(12), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('qty', sa.Integer(), default=1),
        sa.Column('price', sa.Float(), nullable=False),
    )

    op.create_table('expenses',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('category', sa.String(), default='Other'),
        sa.Column('date', sa.Date(), server_default=sa.func.current_date()),
        sa.Column('staff_id', sa.String(12), sa.ForeignKey('staff.id'), nullable=True),
    )

    # 2. Add new columns to existing tables with defaults
    with op.batch_alter_table('products') as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.String(12), sa.ForeignKey('product_categories.id'), nullable=True))
        batch_op.add_column(sa.Column('supplier_id', sa.String(12), sa.ForeignKey('suppliers.id'), nullable=True))
        batch_op.add_column(sa.Column('reserved_stock', sa.Integer(), default=0))
        batch_op.add_column(sa.Column('location', sa.String(), default='Main Shelf'))
        batch_op.add_column(sa.Column('last_movement_at', sa.DateTime(), nullable=True))
    
    with op.batch_alter_table('customers') as batch_op:
        batch_op.add_column(sa.Column('communication_preferences', sa.Text(), default='{}')) # JSON

    with op.batch_alter_table('repairs') as batch_op:
        batch_op.add_column(sa.Column('imei_1', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('imei_2', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('serial_number', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('device_storage', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('device_color', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('passcode', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('water_damage', sa.Boolean(), default=False))
        batch_op.add_column(sa.Column('accessories_received', sa.Text(), default='')) # JSON list

def downgrade() -> None:
    # Not strictly needed for production, but standard practice
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_column('category_id')
        batch_op.drop_column('supplier_id')
        batch_op.drop_column('reserved_stock')
        batch_op.drop_column('location')
        batch_op.drop_column('last_movement_at')
    
    with op.batch_alter_table('customers') as batch_op:
        batch_op.drop_column('communication_preferences')

    with op.batch_alter_table('repairs') as batch_op:
        batch_op.drop_column('imei_1')
        batch_op.drop_column('imei_2')
        batch_op.drop_column('serial_number')
        batch_op.drop_column('device_storage')
        batch_op.drop_column('device_color')
        batch_op.drop_column('passcode')
        batch_op.drop_column('water_damage')
        batch_op.drop_column('accessories_received')

    op.drop_table('expenses')
    op.drop_table('repair_parts_used')
    op.drop_table('product_movements')
    op.drop_table('purchase_orders')
    op.drop_table('suppliers')
    op.drop_table('product_categories')
