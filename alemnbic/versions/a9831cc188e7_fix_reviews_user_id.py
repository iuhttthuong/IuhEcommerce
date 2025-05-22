"""fix reviews user id

Revision ID: a9831cc188e7
Revises: cfc5ffeaaa71
Create Date: 2025-05-21 22:32:45.193018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = 'a9831cc188e7'
down_revision: Union[str, None] = 'cfc5ffeaaa71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # op.drop_table('reviews')
    # op.execute('DROP TABLE shopping_carts CASCADE')
    # op.execute('DROP TABLE cart_items CASCADE')
    # op.create_table(
    #     "reviews",
    #     sa.Column("review_id", sa.Integer, primary_key=True),
    #     sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id")),
    #     sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.customer_id")),
    #     sa.Column("rating", sa.Integer),
    #     sa.Column("comment", sa.Text),
    #     sa.Column("review_date", sa.DateTime),
    #     sa.Column("likes", sa.Integer),
    #     sa.Column("dislikes", sa.Integer),
    # )
    # op.create_table(
    #     "shopping_carts",
    #     sa.Column("cart_id", sa.Integer, primary_key=True),
    #     sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.customer_id")),
    #     sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    #     sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    # )
    # op.create_table(
    #     "cart_items",
    #     sa.Column("cart_id", sa.Integer, sa.ForeignKey("shopping_carts.cart_id")),
    #     sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id")),
    #     sa.Column("quantity", sa.Integer),
    #     sa.Column("added_at", sa.DateTime, server_default=sa.func.now()),
    #     sa.PrimaryKeyConstraint("cart_id", "product_id")
    # )
    # op.add_column('chat_messages',
    #     sa.Column('message_metadata', JSONB, nullable=True)
    # )
    # op.alter_column('chat_messages', 'sender_id',
    #     existing_type=sa.Integer(),
    #     type_=sa.String(36),
    #     existing_nullable=False,
    #     postgresql_using="sender_id::text"
    # )

    # đổi unit_price thành price
    # op.alter_column('order_details', 'unit_price',
    #                 new_column_name='price',
    #                 existing_type=sa.DECIMAL,
    #                 existing_nullable=False,
    #                 existing_server_default=sa.text('0.00')
    # )

    # sửa shop_id thành nullable
    # op.alter_column('chats', 'shop_id',
    #                 existing_type=sa.Integer(),
    #                 nullable=True)
    
    # thêm "current_stock": product.stock_quantity vào inventories
    op.add_column('inventories', sa.Column('current_stock', sa.Integer(), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('reviews')
    op.drop_table('shopping_carts')
    op.create_table(
        "reviews",
        sa.Column("review_id", sa.Integer, primary_key=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.user_id")),
        sa.Column("rating", sa.Integer),
        sa.Column("comment", sa.Text),
        sa.Column("review_date", sa.DateTime),
        sa.Column("likes", sa.Integer),
        sa.Column("dislikes", sa.Integer),
    )
    op.create_table(
        "shopping_carts",
        sa.Column("cart_id", sa.Integer, primary_key=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.customer_id")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
