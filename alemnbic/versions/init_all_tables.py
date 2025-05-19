"""init all tables

Revision ID: 5d288a0b8f0b
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import TypeDecorator, ARRAY, Float

# Custom vector type for PostgreSQL
class VectorType(TypeDecorator):
    impl = ARRAY(Float)
    
    def __init__(self, dimensions=384, **kw):
        self.dimensions = dimensions
        super(VectorType, self).__init__(**kw)
    
    def process_bind_param(self, value, dialect):
        return value
    
    def process_result_value(self, value, dialect):
        return value

# revision identifiers, used by Alembic.
revision: str = '5d288a0b8f0b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sellers table
    op.execute("""
    CREATE TABLE IF NOT EXISTS sellers (
        seller_id SERIAL NOT NULL,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (seller_id),
        UNIQUE (username),
        UNIQUE (email)
    )
    """)

    # Create products table
    op.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price NUMERIC NOT NULL,
        original_price NUMERIC,
        stock INTEGER NOT NULL DEFAULT 0,
        seller_id INTEGER NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (product_id),
        FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
    )
    """)

    # Create customers table
    op.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id SERIAL NOT NULL,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) NOT NULL,
        full_name VARCHAR(100),
        phone VARCHAR(20),
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (customer_id),
        UNIQUE (username),
        UNIQUE (email)
    )
    """)

    # Create orders table
    op.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id SERIAL NOT NULL,
        customer_id INTEGER NOT NULL,
        order_date TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        total_amount NUMERIC NOT NULL,
        shipping_address TEXT,
        payment_method VARCHAR(50),
        payment_status VARCHAR(50),
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (order_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    # Create shops table
    op.execute("""
    CREATE TABLE IF NOT EXISTS shops (
        seller_id INTEGER NOT NULL,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(100) NOT NULL,
        mail VARCHAR(100),
        address TEXT,
        phone VARCHAR(20),
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (seller_id),
        FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
        UNIQUE (username),
        UNIQUE (mail)
    )
    """)

    # Create product_variants table
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_variants (
        id SERIAL NOT NULL,
        product_id INTEGER,
        sku VARCHAR,
        name VARCHAR,
        price NUMERIC,
        original_price NUMERIC,
        inventory_status VARCHAR,
        thumbnail_url VARCHAR,
        option1 VARCHAR,
        PRIMARY KEY (id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # Create product_embeddings table
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_embeddings (
        embedding_id SERIAL NOT NULL,
        product_id INTEGER NOT NULL,
        embedding_vector FLOAT[],
        embedding_type VARCHAR DEFAULT 'description',
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (embedding_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # Create product_attributes table
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_attributes (
        attribute_id SERIAL NOT NULL,
        product_id INTEGER NOT NULL,
        attribute_name VARCHAR NOT NULL,
        attribute_value VARCHAR NOT NULL,
        is_filterable BOOLEAN DEFAULT false,
        is_searchable BOOLEAN DEFAULT true,
        display_order INTEGER DEFAULT 0,
        PRIMARY KEY (attribute_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # Create product_specifications table
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_specifications (
        specification_id SERIAL NOT NULL,
        product_id INTEGER NOT NULL,
        specification_name VARCHAR NOT NULL,
        specification_value VARCHAR NOT NULL,
        specification_group VARCHAR,
        display_order INTEGER DEFAULT 0,
        PRIMARY KEY (specification_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # Create transactions table
    op.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_code VARCHAR NOT NULL,
        order_id INTEGER,
        customer_id INTEGER,
        amount NUMERIC,
        payment_method VARCHAR,
        payment_status VARCHAR,
        transaction_date TIMESTAMP,
        is_successful BOOLEAN,
        PRIMARY KEY (transaction_code),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    # Create buy_history table
    op.execute("""
    CREATE TABLE IF NOT EXISTS buy_history (
        buy_history_id SERIAL NOT NULL,
        customer_id INTEGER,
        product_id INTEGER,
        order_id INTEGER,
        purchase_date TIMESTAMP,
        quantity INTEGER,
        price NUMERIC,
        PRIMARY KEY (buy_history_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
    """)

    # Create reviews table
    op.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        review_id SERIAL NOT NULL,
        product_id INTEGER,
        customer_id INTEGER,
        rating INTEGER,
        comment TEXT,
        review_date TIMESTAMP,
        likes INTEGER,
        dislikes INTEGER,
        PRIMARY KEY (review_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    # Create users table
    op.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL NOT NULL,
        username VARCHAR NOT NULL,
        email VARCHAR NOT NULL,
        password_hash VARCHAR NOT NULL,
        salt VARCHAR NOT NULL,
        is_active BOOLEAN DEFAULT true,
        is_admin BOOLEAN DEFAULT false,
        last_login TIMESTAMP,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id),
        UNIQUE (username),
        UNIQUE (email)
    )
    """)

    # Create user_roles table
    op.execute("""
    CREATE TABLE IF NOT EXISTS user_roles (
        role_id SERIAL NOT NULL,
        role_name VARCHAR NOT NULL,
        role_description VARCHAR,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (role_id),
        UNIQUE (role_name)
    )
    """)

    # Create wishlists table
    op.execute("""
    CREATE TABLE IF NOT EXISTS wishlists (
        wishlist_id SERIAL NOT NULL,
        customer_id INTEGER,
        name VARCHAR,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (wishlist_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    # Create user_role_assignments table
    op.execute("""
    CREATE TABLE IF NOT EXISTS user_role_assignments (
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        assigned_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, role_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (role_id) REFERENCES user_roles(role_id)
    )
    """)

    # Create sessions table
    op.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id VARCHAR NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        ip_address VARCHAR,
        user_agent VARCHAR,
        PRIMARY KEY (session_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # Create wishlist_items table
    op.execute("""
    CREATE TABLE IF NOT EXISTS wishlist_items (
        wishlist_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        added_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (wishlist_id, product_id),
        FOREIGN KEY (wishlist_id) REFERENCES wishlists(wishlist_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # Create shopping_carts table
    op.execute("""
    CREATE TABLE IF NOT EXISTS shopping_carts (
        cart_id SERIAL NOT NULL,
        customer_id INTEGER,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (cart_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    # Create product_imports table
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_imports (
        import_id SERIAL NOT NULL,
        source VARCHAR NOT NULL,
        import_date TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        import_status VARCHAR DEFAULT 'pending',
        total_products INTEGER DEFAULT 0,
        successful_imports INTEGER DEFAULT 0,
        failed_imports INTEGER DEFAULT 0,
        import_log TEXT,
        PRIMARY KEY (import_id)
    )
    """)

    # Create cart_items table
    op.execute("""
    CREATE TABLE IF NOT EXISTS cart_items (
        cart_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        variant_id INTEGER NOT NULL,
        quantity INTEGER,
        added_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (cart_id, product_id, variant_id),
        FOREIGN KEY (cart_id) REFERENCES shopping_carts(cart_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (variant_id) REFERENCES product_variants(id)
    )
    """)

    # Create coupons table
    op.execute("""
    CREATE TABLE IF NOT EXISTS coupons (
        coupon_id SERIAL NOT NULL,
        code VARCHAR,
        description TEXT,
        discount_type VARCHAR,
        discount_value NUMERIC,
        min_purchase NUMERIC,
        max_discount NUMERIC,
        start_date TIMESTAMP,
        end_date TIMESTAMP,
        is_active BOOLEAN,
        usage_limit INTEGER,
        usage_count INTEGER DEFAULT 0,
        PRIMARY KEY (coupon_id),
        UNIQUE (code)
    )
    """)

    # Create search_logs table
    op.execute("""
    CREATE TABLE IF NOT EXISTS search_logs (
        search_id SERIAL NOT NULL,
        user_id INTEGER,
        customer_id INTEGER,
        search_query VARCHAR NOT NULL,
        search_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        results_count INTEGER,
        clicked_product_id INTEGER,
        session_id VARCHAR,
        PRIMARY KEY (search_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
        FOREIGN KEY (clicked_product_id) REFERENCES products(product_id) ON DELETE SET NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE SET NULL
    )
    """)

    # Create customer_coupons table
    op.execute("""
    CREATE TABLE IF NOT EXISTS customer_coupons (
        customer_id INTEGER NOT NULL,
        coupon_id INTEGER NOT NULL,
        is_used BOOLEAN DEFAULT false,
        used_at TIMESTAMP,
        PRIMARY KEY (customer_id, coupon_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id)
    )
    """)

    # Create customer_addresses table
    op.execute("""
    CREATE TABLE IF NOT EXISTS customer_addresses (
        address_id SERIAL NOT NULL,
        customer_id INTEGER,
        address_line1 VARCHAR,
        address_line2 VARCHAR,
        city VARCHAR,
        state VARCHAR,
        postal_code VARCHAR,
        country VARCHAR,
        is_default BOOLEAN,
        address_type VARCHAR,
        PRIMARY KEY (address_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    # Create product_tags table
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_tags (
        tag_id SERIAL NOT NULL,
        name VARCHAR,
        PRIMARY KEY (tag_id),
        UNIQUE (name)
    )
    """)

    # Create product_tag_relations table
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_tag_relations (
        product_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (product_id, tag_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (tag_id) REFERENCES product_tags(tag_id)
    )
    """)


def downgrade() -> None:
    # Drop tables in reverse order
    tables = [
        'product_tag_relations', 'product_tags', 'customer_addresses', 
        'customer_coupons', 'search_logs', 'coupons', 'cart_items',
        'product_imports', 'shopping_carts', 'wishlist_items', 'sessions',
        'user_role_assignments', 'wishlists', 'user_roles', 'users',
        'reviews', 'buy_history', 'transactions', 'product_specifications',
        'product_attributes', 'product_embeddings', 'product_variants', 'shops',
        'orders', 'customers', 'products', 'sellers'
    ]
    
    for table_name in tables:
        op.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE") 