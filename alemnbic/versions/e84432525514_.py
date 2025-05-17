"""empty message

Revision ID: e84432525514
Revises: 1ef28e6eb8c4
Create Date: 2025-05-16 07:36:28.483973

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e84432525514'
down_revision: Union[str, None] = '1ef28e6eb8c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("review_id", sa.Integer, primary_key=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id")),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.customer_id")),
        sa.Column("rating", sa.Integer),
        sa.Column("comment", sa.Text),
        sa.Column("review_date", sa.DateTime),
        sa.Column("likes", sa.Integer),
        sa.Column("dislikes", sa.Integer),
    )

    op.create_table(
        "wishlists",
        sa.Column("wishlist_id", sa.Integer, primary_key=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.customer_id")),
        sa.Column("name", sa.String),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "wishlist_items",
        sa.Column("wishlist_id", sa.Integer, sa.ForeignKey("wishlists.wishlist_id")),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id")),
        sa.Column("added_at", sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("wishlist_id", "product_id")
    )

    op.create_table(
        "shopping_carts",
        sa.Column("cart_id", sa.Integer, primary_key=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.customer_id")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "cart_items",
        sa.Column("cart_id", sa.Integer, sa.ForeignKey("shopping_carts.cart_id")),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id")),
        sa.Column("quantity", sa.Integer),
        sa.Column("added_at", sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("cart_id", "product_id")
    )

    op.create_table(
        "coupons",
        sa.Column("coupon_id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String, unique=True),
        sa.Column("description", sa.Text),
        sa.Column("discount_type", sa.String),
        sa.Column("discount_value", sa.Numeric),
        sa.Column("min_purchase", sa.Numeric),
        sa.Column("max_discount", sa.Numeric),
        sa.Column("start_date", sa.DateTime),
        sa.Column("end_date", sa.DateTime),
        sa.Column("is_active", sa.Boolean),
        sa.Column("usage_limit", sa.Integer),
        sa.Column("usage_count", sa.Integer, server_default="0")
    )

    op.create_table(
        "customer_coupons",
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.customer_id")),
        sa.Column("coupon_id", sa.Integer, sa.ForeignKey("coupons.coupon_id")),
        sa.Column("is_used", sa.Boolean, server_default=sa.text("false")),
        sa.Column("used_at", sa.DateTime),
        sa.PrimaryKeyConstraint("customer_id", "coupon_id")
    )

    op.create_table(
        "customer_addresses",
        sa.Column("address_id", sa.Integer, primary_key=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.customer_id")),
        sa.Column("address_line1", sa.String),
        sa.Column("address_line2", sa.String),
        sa.Column("city", sa.String),
        sa.Column("state", sa.String),
        sa.Column("postal_code", sa.String),
        sa.Column("country", sa.String),
        sa.Column("is_default", sa.Boolean),
        sa.Column("address_type", sa.String),
    )

    op.create_table(
        "product_tags",
        sa.Column("tag_id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True),
    )

    op.create_table(
        "product_tag_relations",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id")),
        sa.Column("tag_id", sa.Integer, sa.ForeignKey("product_tags.tag_id")),
        sa.PrimaryKeyConstraint("product_id", "tag_id")
    )

def downgrade() -> None:
    op.drop_table("product_tag_relations")
    op.drop_table("product_tags")
    op.drop_table("customer_addresses")
    op.drop_table("customer_coupons")
    op.drop_table("coupons")
    op.drop_table("cart_items")
    op.drop_table("shopping_carts")
    op.drop_table("wishlist_items")
    op.drop_table("wishlists")
    op.drop_table("reviews")
