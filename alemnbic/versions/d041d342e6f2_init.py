"""init

Revision ID: d041d342e6f2
Revises: 
Create Date: 2025-04-29 06:09:07.415223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd041d342e6f2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""create initial tables

Revision ID: xxxx
Revises: 
Create Date: 2023-07-20 00:00:00.000000

"""

def upgrade():
    # Create categories table
    op.create_table('categories',
        sa.Column('category_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('path', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('category_id')
    )

    # Create brands table
    op.create_table('brands',
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('brand_name', sa.String(), nullable=True),
        sa.Column('brand_slug', sa.String(), nullable=True),
        sa.Column('brand_country', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('brand_id')
    )

    # Create sellers table
    op.create_table('sellers',
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('seller_name', sa.String(), nullable=True),
        sa.Column('seller_type', sa.String(), nullable=True),
        sa.Column('seller_link', sa.String(), nullable=True),
        sa.Column('seller_logo_url', sa.String(), nullable=True),
        sa.Column('seller_store_id', sa.Integer(), nullable=True),
        sa.Column('seller_is_best_store', sa.Boolean(), nullable=True),
        sa.Column('is_seller', sa.Boolean(), nullable=True),
        sa.Column('is_seller_in_chat_whitelist', sa.Boolean(), nullable=True),
        sa.Column('is_offline_installment_supported', sa.Boolean(), nullable=True),
        sa.Column('store_rating', sa.Numeric(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('seller_id')
    )

    # Create products table
    op.create_table('products',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('product_short_url', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(), nullable=True),
        sa.Column('original_price', sa.Numeric(), nullable=True),
        sa.Column('discount', sa.Numeric(), nullable=True),
        sa.Column('discount_rate', sa.Integer(), nullable=True),
        sa.Column('sku', sa.String(), nullable=True),
        sa.Column('review_text', sa.String(), nullable=True),
        sa.Column('quantity_sold', sa.Integer(), nullable=True),
        sa.Column('rating_average', sa.Numeric(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('order_count', sa.Integer(), nullable=True),
        sa.Column('favourite_count', sa.Integer(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('category_id', sa.String(), nullable=True),
        sa.Column('brand_id', sa.Integer(), nullable=True),
        sa.Column('seller_id', sa.Integer(), nullable=True),
        sa.Column('shippable', sa.Boolean(), nullable=True),
        sa.Column('availability', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('product_id'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.category_id']),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.brand_id']),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.seller_id'])
    )

    # Create product_images table
    op.create_table('product_images',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('base_url', sa.String(), nullable=True),
        sa.Column('large_url', sa.String(), nullable=True),
        sa.Column('medium_url', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id']),
    )

    # Create warranties table

    op.create_table('warranties',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('warranty_location', sa.String(), nullable=True),
    sa.Column('warranty_period', sa.String(), nullable=True),
    sa.Column('warranty_form', sa.String(), nullable=True),
    sa.Column('warranty_url', sa.String(), nullable=True),
    sa.Column('return_policy', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('product_id'),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'])
)

    # Create customers table
    op.create_table('customers',
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('customer_fname', sa.String(), nullable=True),
        sa.Column('customer_lname', sa.String(), nullable=True),
        sa.Column('customer_mail', sa.String(), nullable=True),
        sa.Column('customer_address', sa.String(), nullable=True),
        sa.Column('customer_phone', sa.String(), nullable=True),
        sa.Column('customer_dob', sa.Date(), nullable=True),
        sa.Column('customer_gender', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('customer_id')
    )

    # Create orders table
    op.create_table('orders',
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('order_status', sa.String(), nullable=True),
        sa.Column('total_amount', sa.Numeric(), nullable=True),
        sa.Column('order_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('payment_method', sa.String(), nullable=True),
        sa.Column('delivery_method', sa.String(), nullable=True),
        sa.Column('delivery_fee', sa.Numeric(), nullable=True),
        sa.Column('discount_amount', sa.Numeric(), nullable=True),
        sa.Column('transaction_code', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('order_id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'])
    )

    # Create order_details table
    op.create_table('order_details',
        sa.Column('order_detail_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('unit_price', sa.Numeric(), nullable=True),
        sa.Column('discount', sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint('order_detail_id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'])
    )

    # Create inventory table
    op.create_table('inventories',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_virtual_type', sa.String(), nullable=True),
        sa.Column('fulfillment_type', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('product_id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'])
    )

    # Create shipping_info table
    op.create_table('shipping_info',
        sa.Column('shipping_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('shipping_status', sa.String(), nullable=True),
        sa.Column('estimated_delivery', sa.TIMESTAMP(), nullable=True),
        sa.Column('tracking_number', sa.String(), nullable=True),
        sa.Column('carrier', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('shipping_id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'])
    )

    # Create discounts table
    op.create_table('discounts',
        sa.Column('discount_id', sa.Integer(), nullable=False),
        sa.Column('discount_name', sa.String(), nullable=True),
        sa.Column('discount_rate', sa.Numeric(), nullable=True),
        sa.Column('start_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('end_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('min_purchase_amount', sa.Numeric(), nullable=True),
        sa.Column('max_discount_amount', sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint('discount_id')
    )

    # Create product_discounts table
    op.create_table('product_discounts',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('discount_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('product_id', 'discount_id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id']),
        sa.ForeignKeyConstraint(['discount_id'], ['discounts.discount_id'])
    )

    # Create transactions table
    op.create_table('transactions',
        sa.Column('transaction_code', sa.String(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(), nullable=True),
        sa.Column('payment_method', sa.String(), nullable=True),
        sa.Column('payment_status', sa.String(), nullable=True),
        sa.Column('transaction_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('is_successful', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('transaction_code'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'])
    )

    # Create buy_history table
    op.create_table('buy_history',
        sa.Column('buy_history_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('purchase_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('price', sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint('buy_history_id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'])
    )


def downgrade():
    # Drop all tables in reverse order of creation
    op.drop_table('buy_history')
    op.drop_table('transactions')
    op.drop_table('product_discounts')
    op.drop_table('discounts')
    op.drop_table('shipping_info')
    op.drop_table('inventories')
    op.drop_table('order_details')
    op.drop_table('orders')
    op.drop_table('customers')
    op.drop_table('warranties')
    op.drop_table('product_images')
    op.drop_table('products')
    op.drop_table('sellers')
    op.drop_table('brands')
    op.drop_table('categories')