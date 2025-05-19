from logging.config import fileConfig

import os
from dotenv import load_dotenv

# Nạp các biến môi trường từ file .env
load_dotenv()

# Lấy các giá trị từ biến môi trường
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Tạo chuỗi kết nối
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Sử dụng chuỗi kết nối trong Alembic
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import Base và các models
from models.base import Base
from models.sellers import Seller
from models.products import Product
from models.customers import Customer
from models.orders import Order
from models.shop import Shop
from models.product_embeddings import ProductEmbedding
from models.product_attributes import ProductAttribute
from models.product_specifications import ProductSpecification
from models.transactions import Transaction
from models.buy_history import BuyHistory
from models.reviews import Review
from models.user import User
from models.user_roles import UserRole
from models.wishlists import Wishlist
from models.user_role_assignments import UserRoleAssignment
from models.sessions import Session
from models.wishlist_items import WishlistItem
from models.shopping_carts import ShoppingCart
from models.product_imports import ProductImport
from models.cart_items import CartItem
from models.coupons import Coupon
from models.search_logs import SearchLog
from models.customer_coupons import CustomerCoupon
from models.customer_addresses import CustomerAddress
from models.product_tags import ProductTag
from models.product_tag_relations import ProductTagRelation
from models.categories import Category
from models.chat import Chat

config = context.config
config.set_section_option('alembic', 'sqlalchemy.url', SQLALCHEMY_DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
