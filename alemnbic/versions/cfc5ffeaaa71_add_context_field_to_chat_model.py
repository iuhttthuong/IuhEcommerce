"""Add context field to Chat model

Revision ID: cfc5ffeaaa71
Revises: 39eadb05536a
Create Date: 2025-05-21 17:13:43.966406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cfc5ffeaaa71'
down_revision: Union[str, None] = '39eadb05536a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get connection
    connection = op.get_bind()
    
    # Create enum types first
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Create transaction status enum if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transactionstatus') THEN
                CREATE TYPE transactionstatus AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED', 'CANCELLED');
            END IF;
            
            -- Create transaction type enum if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transactiontype') THEN
                CREATE TYPE transactiontype AS ENUM ('PURCHASE', 'REFUND', 'WITHDRAWAL', 'DEPOSIT');
            END IF;
        END $$;
    """))
    
    # Add context field to chats table if it doesn't exist and set default for last_message_at
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Add context column if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'chats' AND column_name = 'context'
            ) THEN
                ALTER TABLE chats ADD COLUMN context JSONB;
            END IF;
            
            -- Set default value for last_message_at if it's NULL
            UPDATE chats SET last_message_at = CURRENT_TIMESTAMP WHERE last_message_at IS NULL;
            
            -- Alter last_message_at to have default value and NOT NULL constraint
            ALTER TABLE chats ALTER COLUMN last_message_at SET DEFAULT CURRENT_TIMESTAMP;
            ALTER TABLE chats ALTER COLUMN last_message_at SET NOT NULL;
        END $$;
    """))
    
    # Handle sessions table modifications safely
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Add new columns if they don't exist
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'token'
            ) THEN
                ALTER TABLE sessions ADD COLUMN token VARCHAR;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'device_info'
            ) THEN
                ALTER TABLE sessions ADD COLUMN device_info VARCHAR;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'is_active'
            ) THEN
                ALTER TABLE sessions ADD COLUMN is_active BOOLEAN DEFAULT true;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'last_activity'
            ) THEN
                ALTER TABLE sessions ADD COLUMN last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'session_metadata'
            ) THEN
                ALTER TABLE sessions ADD COLUMN session_metadata JSONB;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE sessions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            END IF;
            
            -- Update existing columns to be NOT NULL if they are NULL
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'token' AND is_nullable = 'YES'
            ) THEN
                UPDATE sessions SET token = md5(random()::text) WHERE token IS NULL;
                ALTER TABLE sessions ALTER COLUMN token SET NOT NULL;
            END IF;
            
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'is_active' AND is_nullable = 'YES'
            ) THEN
                UPDATE sessions SET is_active = true WHERE is_active IS NULL;
                ALTER TABLE sessions ALTER COLUMN is_active SET NOT NULL;
            END IF;
            
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'last_activity' AND is_nullable = 'YES'
            ) THEN
                UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE last_activity IS NULL;
                ALTER TABLE sessions ALTER COLUMN last_activity SET NOT NULL;
            END IF;
            
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'updated_at' AND is_nullable = 'YES'
            ) THEN
                UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL;
                ALTER TABLE sessions ALTER COLUMN updated_at SET NOT NULL;
            END IF;
        END $$;
    """))
    
    # Handle products table modifications
    connection.execute(sa.text("""
        DO $$ 
        DECLARE
            default_brand_id INTEGER;
            default_seller_id INTEGER;
            missing_seller RECORD;
        BEGIN
            -- First, check if we have any brands
            SELECT brand_id INTO default_brand_id FROM brands LIMIT 1;
            IF default_brand_id IS NULL THEN
                -- Create a default brand if none exists
                INSERT INTO brands (brand_name, created_at, updated_at)
                VALUES ('Default Brand', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING brand_id INTO default_brand_id;
            END IF;
            
            -- Check if we have any sellers
            SELECT seller_id INTO default_seller_id FROM sellers LIMIT 1;
            IF default_seller_id IS NULL THEN
                -- Create a default seller if none exists
                INSERT INTO sellers (seller_name, created_at, updated_at)
                VALUES ('Default Seller', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING seller_id INTO default_seller_id;
            END IF;
            
            -- Find all missing sellers and create them
            FOR missing_seller IN 
                SELECT DISTINCT p.seller_id 
                FROM products p 
                LEFT JOIN sellers s ON p.seller_id = s.seller_id 
                WHERE s.seller_id IS NULL AND p.seller_id IS NOT NULL
            LOOP
                INSERT INTO sellers (seller_id, seller_name, created_at, updated_at)
                VALUES (missing_seller.seller_id, 'Seller ' || missing_seller.seller_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (seller_id) DO NOTHING;
            END LOOP;
            
            -- Update NULL values with valid foreign keys
            UPDATE products SET brand_id = default_brand_id WHERE brand_id IS NULL;
            UPDATE products SET seller_id = default_seller_id WHERE seller_id IS NULL;
            UPDATE products SET category_id = 'default' WHERE category_id IS NULL;
            
            -- Now we can safely alter the columns to be non-nullable
            ALTER TABLE products ALTER COLUMN brand_id TYPE INTEGER USING brand_id::INTEGER;
            ALTER TABLE products ALTER COLUMN brand_id SET NOT NULL;
            
            ALTER TABLE products ALTER COLUMN seller_id TYPE INTEGER USING seller_id::INTEGER;
            ALTER TABLE products ALTER COLUMN seller_id SET NOT NULL;
            
            ALTER TABLE products ALTER COLUMN category_id SET NOT NULL;
        END $$;
    """))
    
    # Safely convert session_id from VARCHAR to INTEGER
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Drop foreign key constraints first
            ALTER TABLE search_logs DROP CONSTRAINT IF EXISTS search_logs_session_id_fkey;
            
            -- Create a temporary column
            ALTER TABLE sessions ADD COLUMN session_id_new SERIAL;
            
            -- Convert the data
            UPDATE sessions SET session_id_new = session_id::INTEGER;
            
            -- Drop the old column and rename the new one
            ALTER TABLE sessions DROP COLUMN session_id;
            ALTER TABLE sessions RENAME COLUMN session_id_new TO session_id;
            
            -- Make it the primary key
            ALTER TABLE sessions ADD PRIMARY KEY (session_id);
            
            -- Update search_logs table to use INTEGER
            ALTER TABLE search_logs ALTER COLUMN session_id TYPE INTEGER USING session_id::INTEGER;
            
            -- Recreate the foreign key constraint
            ALTER TABLE search_logs ADD CONSTRAINT search_logs_session_id_fkey 
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE;
        END $$;
    """))
    
    # Continue with other table modifications...
    op.add_column('product_embeddings', sa.Column('embedding_metadata', sa.JSON(), nullable=True))
    op.alter_column('product_embeddings', 'embedding_type',
               existing_type=sa.VARCHAR(),
               nullable=False,
               existing_server_default=sa.text("'description'::character varying"))
    op.alter_column('product_embeddings', 'embedding_vector',
               existing_type=postgresql.ARRAY(sa.DOUBLE_PRECISION(precision=53)),
               nullable=False)
    op.alter_column('product_embeddings', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('product_embeddings', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.create_foreign_key(None, 'product_embeddings', 'products', ['product_id'], ['product_id'])
    op.add_column('product_imports', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('product_imports', sa.Column('status', sa.String(), nullable=False))
    op.add_column('product_imports', sa.Column('imported_products', sa.Integer(), nullable=False))
    op.add_column('product_imports', sa.Column('failed_products', sa.Integer(), nullable=False))
    op.add_column('product_imports', sa.Column('import_metadata', sa.JSON(), nullable=True))
    op.add_column('product_imports', sa.Column('error_message', sa.String(), nullable=True))
    op.add_column('product_imports', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('product_imports', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('product_imports', 'total_products',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))
    op.create_foreign_key(None, 'product_imports', 'users', ['user_id'], ['user_id'])
    op.drop_column('product_imports', 'source')
    op.drop_column('product_imports', 'failed_imports')
    op.drop_column('product_imports', 'successful_imports')
    op.drop_column('product_imports', 'import_date')
    op.drop_column('product_imports', 'import_status')
    op.drop_column('product_imports', 'import_log')
    op.add_column('product_specifications', sa.Column('category', sa.String(), nullable=False))
    op.add_column('product_specifications', sa.Column('specifications', sa.JSON(), nullable=False))
    op.add_column('product_specifications', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('product_specifications', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('product_specifications', 'display_order',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))
    op.create_foreign_key(None, 'product_specifications', 'products', ['product_id'], ['product_id'])
    op.drop_column('product_specifications', 'specification_name')
    op.drop_column('product_specifications', 'specification_value')
    op.drop_column('product_specifications', 'specification_group')
    op.add_column('product_tag_relations', sa.Column('relation_id', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('product_tag_relations', sa.Column('relation_metadata', sa.JSON(), nullable=True))
    op.add_column('product_tag_relations', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('product_tag_relations', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_foreign_key(None, 'product_tag_relations', 'products', ['product_id'], ['product_id'])
    op.add_column('product_tags', sa.Column('slug', sa.String(), nullable=False))
    op.add_column('product_tags', sa.Column('description', sa.String(), nullable=True))
    op.add_column('product_tags', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('product_tags', sa.Column('tag_metadata', sa.JSON(), nullable=True))
    op.add_column('product_tags', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('product_tags', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('product_tags', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.create_unique_constraint(None, 'product_tags', ['slug'])
    op.alter_column('products', 'product_id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=False)
    op.alter_column('products', 'name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('products', 'product_short_url',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('products', 'description',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('products', 'short_description',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('products', 'discount_rate',
               existing_type=sa.NUMERIC(),
               type_=sa.Integer(),
               existing_nullable=True)
    op.alter_column('products', 'review_text',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('products', 'thumbnail_url',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('products', 'category_id',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('products', 'brand_id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False)
    op.alter_column('products', 'seller_id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False)
    op.alter_column('products', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('products', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.create_foreign_key(None, 'products', 'sellers', ['seller_id'], ['seller_id'])
    op.add_column('reviews', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('reviews', sa.Column('title', sa.String(), nullable=True))
    op.add_column('reviews', sa.Column('content', sa.String(), nullable=False))
    op.add_column('reviews', sa.Column('images', sa.JSON(), nullable=True))
    op.add_column('reviews', sa.Column('is_verified_purchase', sa.Boolean(), nullable=False))
    op.add_column('reviews', sa.Column('helpful_votes', sa.Integer(), nullable=False))
    op.add_column('reviews', sa.Column('review_metadata', sa.JSON(), nullable=True))
    op.add_column('reviews', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('reviews', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('reviews', 'product_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('reviews', 'rating',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               nullable=False)
    op.alter_column('reviews', 'likes',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint('reviews_customer_id_fkey', 'reviews', type_='foreignkey')
    op.create_foreign_key(None, 'reviews', 'users', ['user_id'], ['user_id'])
    op.create_foreign_key(None, 'reviews', 'products', ['product_id'], ['product_id'])
    op.drop_column('reviews', 'comment')
    op.drop_column('reviews', 'review_date')
    op.drop_column('reviews', 'dislikes')
    op.drop_column('reviews', 'customer_id')
    op.add_column('search_logs', sa.Column('log_id', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('search_logs', sa.Column('query', sa.String(), nullable=False))
    op.add_column('search_logs', sa.Column('filters', sa.JSON(), nullable=True))
    op.add_column('search_logs', sa.Column('result_count', sa.Integer(), nullable=False))
    op.add_column('search_logs', sa.Column('ip_address', sa.String(), nullable=True))
    op.add_column('search_logs', sa.Column('user_agent', sa.String(), nullable=True))
    op.add_column('search_logs', sa.Column('search_metadata', sa.JSON(), nullable=True))
    op.add_column('search_logs', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('search_logs', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.drop_constraint('search_logs_user_id_fkey', 'search_logs', type_='foreignkey')
    op.drop_constraint('search_logs_session_id_fkey', 'search_logs', type_='foreignkey')
    op.drop_constraint('search_logs_customer_id_fkey', 'search_logs', type_='foreignkey')
    op.create_foreign_key(None, 'search_logs', 'users', ['user_id'], ['user_id'])
    op.drop_column('search_logs', 'results_count')
    op.drop_column('search_logs', 'session_id')
    op.drop_column('search_logs', 'search_id')
    op.drop_column('search_logs', 'clicked_product_id')
    op.drop_column('search_logs', 'search_query')
    op.drop_column('search_logs', 'search_timestamp')
    op.drop_column('search_logs', 'customer_id')
    op.alter_column('sellers', 'seller_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sellers', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('sellers', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('sessions', 'session_id',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('sessions', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.create_unique_constraint(None, 'sessions', ['token'])
    op.drop_column('sessions', 'user_agent')
    op.add_column('shopping_carts', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('shopping_carts', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('shopping_carts', sa.Column('cart_metadata', sa.JSON(), nullable=True))
    op.alter_column('shopping_carts', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('shopping_carts', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.drop_constraint('shopping_carts_customer_id_fkey', 'shopping_carts', type_='foreignkey')
    op.create_foreign_key(None, 'shopping_carts', 'users', ['user_id'], ['user_id'])
    op.drop_column('shopping_carts', 'customer_id')
    op.alter_column('shops', 'username',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.alter_column('shops', 'password',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('shops', 'email',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('shops', 'shop_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('shops', 'description',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('shops', 'address',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('shops', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
    op.alter_column('shops', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('shops', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.add_column('transactions', sa.Column('transaction_id', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('transactions', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('transactions', sa.Column('currency', sa.String(length=3), nullable=False))
    op.add_column('transactions', sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED', 'CANCELLED', name='transactionstatus'), nullable=False))
    op.add_column('transactions', sa.Column('type', sa.Enum('PURCHASE', 'REFUND', 'WITHDRAWAL', 'DEPOSIT', name='transactiontype'), nullable=False))
    op.add_column('transactions', sa.Column('payment_id', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('description', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('transaction_metadata', sa.JSON(), nullable=True))
    op.add_column('transactions', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('transactions', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('transactions', 'amount',
               existing_type=sa.NUMERIC(),
               nullable=False)
    op.drop_constraint('transactions_order_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_customer_id_fkey', 'transactions', type_='foreignkey')
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['user_id'])
    op.drop_column('transactions', 'payment_status')
    op.drop_column('transactions', 'is_successful')
    op.drop_column('transactions', 'order_id')
    op.drop_column('transactions', 'transaction_date')
    op.drop_column('transactions', 'customer_id')
    op.drop_column('transactions', 'transaction_code')
    op.add_column('user_role_assignments', sa.Column('assignment_id', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('user_role_assignments', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('user_role_assignments', sa.Column('assigned_by', sa.Integer(), nullable=True))
    op.add_column('user_role_assignments', sa.Column('assignment_metadata', sa.JSON(), nullable=True))
    op.add_column('user_role_assignments', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('user_role_assignments', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_foreign_key(None, 'user_role_assignments', 'users', ['assigned_by'], ['user_id'])
    op.drop_column('user_role_assignments', 'assigned_at')
    op.add_column('user_roles', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('user_roles', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('user_roles', sa.Column('description', sa.String(), nullable=True))
    op.add_column('user_roles', sa.Column('permissions', sa.String(), nullable=True))
    op.add_column('user_roles', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('user_roles', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.drop_constraint('user_roles_role_name_key', 'user_roles', type_='unique')
    op.create_foreign_key(None, 'user_roles', 'users', ['user_id'], ['user_id'])
    op.drop_column('user_roles', 'role_description')
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=False))
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('user_metadata', sa.JSON(), nullable=True))
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'salt')
    op.add_column('wishlist_items', sa.Column('item_id', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('wishlist_items', sa.Column('quantity', sa.Integer(), nullable=False))
    op.add_column('wishlist_items', sa.Column('notes', sa.String(), nullable=True))
    op.add_column('wishlist_items', sa.Column('priority', sa.Integer(), nullable=False))
    op.add_column('wishlist_items', sa.Column('is_notified', sa.Boolean(), nullable=False))
    op.add_column('wishlist_items', sa.Column('item_metadata', sa.JSON(), nullable=True))
    op.add_column('wishlist_items', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('wishlist_items', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_foreign_key(None, 'wishlist_items', 'products', ['product_id'], ['product_id'])
    op.drop_column('wishlist_items', 'added_at')
    op.add_column('wishlists', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('wishlists', sa.Column('description', sa.String(), nullable=True))
    op.add_column('wishlists', sa.Column('is_public', sa.Boolean(), nullable=False))
    op.add_column('wishlists', sa.Column('is_default', sa.Boolean(), nullable=False))
    op.add_column('wishlists', sa.Column('wishlist_metadata', sa.JSON(), nullable=True))
    op.alter_column('wishlists', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('wishlists', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('wishlists', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.drop_constraint('wishlists_customer_id_fkey', 'wishlists', type_='foreignkey')
    op.create_foreign_key(None, 'wishlists', 'users', ['user_id'], ['user_id'])
    op.drop_column('wishlists', 'customer_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wishlists', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'wishlists', type_='foreignkey')
    op.create_foreign_key('wishlists_customer_id_fkey', 'wishlists', 'customers', ['customer_id'], ['customer_id'])
    op.alter_column('wishlists', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('wishlists', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('wishlists', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('wishlists', 'wishlist_metadata')
    op.drop_column('wishlists', 'is_default')
    op.drop_column('wishlists', 'is_public')
    op.drop_column('wishlists', 'description')
    op.drop_column('wishlists', 'user_id')
    op.add_column('wishlist_items', sa.Column('added_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'wishlist_items', type_='foreignkey')
    op.drop_column('wishlist_items', 'updated_at')
    op.drop_column('wishlist_items', 'created_at')
    op.drop_column('wishlist_items', 'item_metadata')
    op.drop_column('wishlist_items', 'is_notified')
    op.drop_column('wishlist_items', 'priority')
    op.drop_column('wishlist_items', 'notes')
    op.drop_column('wishlist_items', 'quantity')
    op.drop_column('wishlist_items', 'item_id')
    op.add_column('users', sa.Column('salt', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('is_admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=True))
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
    op.drop_column('users', 'user_metadata')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'hashed_password')
    op.add_column('user_roles', sa.Column('role_description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user_roles', type_='foreignkey')
    op.create_unique_constraint('user_roles_role_name_key', 'user_roles', ['role_name'])
    op.alter_column('user_roles', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.drop_column('user_roles', 'updated_at')
    op.drop_column('user_roles', 'permissions')
    op.drop_column('user_roles', 'description')
    op.drop_column('user_roles', 'is_active')
    op.drop_column('user_roles', 'user_id')
    op.add_column('user_role_assignments', sa.Column('assigned_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user_role_assignments', type_='foreignkey')
    op.drop_column('user_role_assignments', 'updated_at')
    op.drop_column('user_role_assignments', 'created_at')
    op.drop_column('user_role_assignments', 'assignment_metadata')
    op.drop_column('user_role_assignments', 'assigned_by')
    op.drop_column('user_role_assignments', 'is_active')
    op.drop_column('user_role_assignments', 'assignment_id')
    op.add_column('transactions', sa.Column('transaction_code', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('transactions', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('transactions', sa.Column('transaction_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('transactions', sa.Column('order_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('transactions', sa.Column('is_successful', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('transactions', sa.Column('payment_status', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.create_foreign_key('transactions_customer_id_fkey', 'transactions', 'customers', ['customer_id'], ['customer_id'])
    op.create_foreign_key('transactions_order_id_fkey', 'transactions', 'orders', ['order_id'], ['order_id'])
    op.alter_column('transactions', 'amount',
               existing_type=sa.NUMERIC(),
               nullable=True)
    op.drop_column('transactions', 'updated_at')
    op.drop_column('transactions', 'created_at')
    op.drop_column('transactions', 'transaction_metadata')
    op.drop_column('transactions', 'description')
    op.drop_column('transactions', 'payment_id')
    op.drop_column('transactions', 'type')
    op.drop_column('transactions', 'status')
    op.drop_column('transactions', 'currency')
    op.drop_column('transactions', 'user_id')
    op.drop_column('transactions', 'transaction_id')
    op.alter_column('shops', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('shops', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('shops', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
    op.alter_column('shops', 'address',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('shops', 'description',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('shops', 'shop_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('shops', 'email',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('shops', 'password',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('shops', 'username',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.add_column('shopping_carts', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'shopping_carts', type_='foreignkey')
    op.create_foreign_key('shopping_carts_customer_id_fkey', 'shopping_carts', 'customers', ['customer_id'], ['customer_id'])
    op.alter_column('shopping_carts', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('shopping_carts', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.drop_column('shopping_carts', 'cart_metadata')
    op.drop_column('shopping_carts', 'is_active')
    op.drop_column('shopping_carts', 'user_id')
    op.add_column('sessions', sa.Column('user_agent', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'sessions', type_='unique')
    op.alter_column('sessions', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('sessions', 'session_id',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=False,
               autoincrement=True)
    op.drop_column('sessions', 'updated_at')
    op.drop_column('sessions', 'session_metadata')
    op.drop_column('sessions', 'last_activity')
    op.drop_column('sessions', 'is_active')
    op.drop_column('sessions', 'device_info')
    op.drop_column('sessions', 'token')
    op.alter_column('sellers', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('sellers', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('sellers', 'seller_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.add_column('search_logs', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('search_logs', sa.Column('search_timestamp', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True))
    op.add_column('search_logs', sa.Column('search_query', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('search_logs', sa.Column('clicked_product_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('search_logs', sa.Column('search_id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.add_column('search_logs', sa.Column('session_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('search_logs', sa.Column('results_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'search_logs', type_='foreignkey')
    op.create_foreign_key('search_logs_customer_id_fkey', 'search_logs', 'customers', ['customer_id'], ['customer_id'], ondelete='SET NULL')
    op.create_foreign_key('search_logs_session_id_fkey', 'search_logs', 'sessions', ['session_id'], ['session_id'], ondelete='SET NULL')
    op.create_foreign_key('search_logs_user_id_fkey', 'search_logs', 'users', ['user_id'], ['user_id'], ondelete='SET NULL')
    op.drop_column('search_logs', 'updated_at')
    op.drop_column('search_logs', 'created_at')
    op.drop_column('search_logs', 'search_metadata')
    op.drop_column('search_logs', 'user_agent')
    op.drop_column('search_logs', 'ip_address')
    op.drop_column('search_logs', 'result_count')
    op.drop_column('search_logs', 'filters')
    op.drop_column('search_logs', 'query')
    op.drop_column('search_logs', 'log_id')
    op.add_column('reviews', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('reviews', sa.Column('dislikes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('reviews', sa.Column('review_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('reviews', sa.Column('comment', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'reviews', type_='foreignkey')
    op.drop_constraint(None, 'reviews', type_='foreignkey')
    op.create_foreign_key('reviews_customer_id_fkey', 'reviews', 'customers', ['customer_id'], ['customer_id'])
    op.alter_column('reviews', 'likes',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('reviews', 'rating',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               nullable=True)
    op.alter_column('reviews', 'product_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('reviews', 'updated_at')
    op.drop_column('reviews', 'created_at')
    op.drop_column('reviews', 'review_metadata')
    op.drop_column('reviews', 'helpful_votes')
    op.drop_column('reviews', 'is_verified_purchase')
    op.drop_column('reviews', 'images')
    op.drop_column('reviews', 'content')
    op.drop_column('reviews', 'title')
    op.drop_column('reviews', 'user_id')
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.alter_column('products', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('products', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('products', 'seller_id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True)
    op.alter_column('products', 'brand_id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True)
    op.alter_column('products', 'category_id',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('products', 'thumbnail_url',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('products', 'review_text',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('products', 'discount_rate',
               existing_type=sa.Integer(),
               type_=sa.NUMERIC(),
               existing_nullable=True)
    op.alter_column('products', 'short_description',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('products', 'description',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('products', 'product_short_url',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('products', 'name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('products', 'product_id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=False,
               autoincrement=False)
    op.drop_constraint(None, 'product_tags', type_='unique')
    op.alter_column('product_tags', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('product_tags', 'updated_at')
    op.drop_column('product_tags', 'created_at')
    op.drop_column('product_tags', 'tag_metadata')
    op.drop_column('product_tags', 'is_active')
    op.drop_column('product_tags', 'description')
    op.drop_column('product_tags', 'slug')
    op.drop_constraint(None, 'product_tag_relations', type_='foreignkey')
    op.drop_column('product_tag_relations', 'updated_at')
    op.drop_column('product_tag_relations', 'created_at')
    op.drop_column('product_tag_relations', 'relation_metadata')
    op.drop_column('product_tag_relations', 'relation_id')
    op.add_column('product_specifications', sa.Column('specification_group', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('product_specifications', sa.Column('specification_value', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('product_specifications', sa.Column('specification_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'product_specifications', type_='foreignkey')
    op.alter_column('product_specifications', 'display_order',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.drop_column('product_specifications', 'updated_at')
    op.drop_column('product_specifications', 'created_at')
    op.drop_column('product_specifications', 'specifications')
    op.drop_column('product_specifications', 'category')
    op.add_column('product_imports', sa.Column('import_log', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('product_imports', sa.Column('import_status', sa.VARCHAR(), server_default=sa.text("'pending'::character varying"), autoincrement=False, nullable=True))
    op.add_column('product_imports', sa.Column('import_date', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True))
    op.add_column('product_imports', sa.Column('successful_imports', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True))
    op.add_column('product_imports', sa.Column('failed_imports', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True))
    op.add_column('product_imports', sa.Column('source', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'product_imports', type_='foreignkey')
    op.alter_column('product_imports', 'total_products',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.drop_column('product_imports', 'updated_at')
    op.drop_column('product_imports', 'created_at')
    op.drop_column('product_imports', 'error_message')
    op.drop_column('product_imports', 'import_metadata')
    op.drop_column('product_imports', 'failed_products')
    op.drop_column('product_imports', 'imported_products')
    op.drop_column('product_imports', 'status')
    op.drop_column('product_imports', 'user_id')
    op.drop_constraint(None, 'product_embeddings', type_='foreignkey')
    op.alter_column('product_embeddings', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('product_embeddings', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('product_embeddings', 'embedding_vector',
               existing_type=postgresql.ARRAY(sa.DOUBLE_PRECISION(precision=53)),
               nullable=True)
    op.alter_column('product_embeddings', 'embedding_type',
               existing_type=sa.VARCHAR(),
               nullable=True,
               existing_server_default=sa.text("'description'::character varying"))
    op.drop_column('product_embeddings', 'embedding_metadata')
    op.add_column('product_attributes', sa.Column('is_filterable', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=True))
    op.add_column('product_attributes', sa.Column('attribute_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('product_attributes', sa.Column('is_searchable', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=True))
    op.add_column('product_attributes', sa.Column('attribute_value', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'product_attributes', type_='foreignkey')
    op.alter_column('product_attributes', 'display_order',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.drop_column('product_attributes', 'updated_at')
    op.drop_column('product_attributes', 'created_at')
    op.drop_column('product_attributes', 'unit')
    op.drop_column('product_attributes', 'value')
    op.drop_column('product_attributes', 'name')
    op.add_column('orders', sa.Column('transaction_code', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('order_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('delivery_fee', sa.NUMERIC(), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('discount_amount', sa.NUMERIC(), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('order_status', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('delivery_method', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('orders', 'payment_method',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('orders', 'total_amount',
               existing_type=sa.NUMERIC(),
               nullable=True)
    op.alter_column('orders', 'customer_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('orders', 'updated_at')
    op.drop_column('orders', 'created_at')
    op.drop_column('orders', 'notes')
    op.drop_column('orders', 'tracking_number')
    op.drop_column('orders', 'payment_status')
    op.drop_column('orders', 'shipping_address')
    op.drop_column('orders', 'status')
    op.drop_constraint(None, 'customers', type_='unique')
    op.alter_column('customers', 'customer_gender',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customers', 'customer_dob',
               existing_type=sa.String(length=20),
               type_=sa.DATE(),
               nullable=True)
    op.alter_column('customers', 'customer_phone',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customers', 'customer_address',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customers', 'customer_mail',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customers', 'customer_lname',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customers', 'customer_fname',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.add_column('customer_coupons', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'customer_coupons', type_='foreignkey')
    op.drop_constraint(None, 'customer_coupons', type_='foreignkey')
    op.create_foreign_key('customer_coupons_customer_id_fkey', 'customer_coupons', 'customers', ['customer_id'], ['customer_id'])
    op.alter_column('customer_coupons', 'is_used',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.drop_column('customer_coupons', 'updated_at')
    op.drop_column('customer_coupons', 'created_at')
    op.drop_column('customer_coupons', 'customer_coupon_metadata')
    op.drop_column('customer_coupons', 'order_id')
    op.drop_column('customer_coupons', 'user_id')
    op.drop_column('customer_coupons', 'id')
    op.add_column('customer_addresses', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'customer_addresses', type_='foreignkey')
    op.create_foreign_key('customer_addresses_customer_id_fkey', 'customer_addresses', 'customers', ['customer_id'], ['customer_id'])
    op.alter_column('customer_addresses', 'address_type',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customer_addresses', 'is_default',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('customer_addresses', 'country',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customer_addresses', 'postal_code',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customer_addresses', 'state',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customer_addresses', 'city',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('customer_addresses', 'address_line1',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('customer_addresses', 'updated_at')
    op.drop_column('customer_addresses', 'created_at')
    op.drop_column('customer_addresses', 'address_metadata')
    op.drop_column('customer_addresses', 'phone_number')
    op.drop_column('customer_addresses', 'full_name')
    op.drop_column('customer_addresses', 'user_id')
    op.add_column('coupons', sa.Column('min_purchase', sa.NUMERIC(), autoincrement=False, nullable=True))
    op.alter_column('coupons', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('coupons', 'usage_count',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.alter_column('coupons', 'end_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('coupons', 'start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('coupons', 'discount_value',
               existing_type=sa.NUMERIC(),
               nullable=True)
    op.alter_column('coupons', 'discount_type',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('coupons', 'description',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('coupons', 'code',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('coupons', 'updated_at')
    op.drop_column('coupons', 'created_at')
    op.drop_column('coupons', 'coupon_metadata')
    op.drop_column('coupons', 'min_order_value')
    op.alter_column('chats', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('chats', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_column('chats', 'context')
    op.alter_column('chat_messages', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('chat_messages', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('chat_messages', 'content',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.add_column('categories', sa.Column('parent_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('categories', sa.Column('level', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('categories_parent_id_fkey', 'categories', 'categories', ['parent_id'], ['category_id'])
    op.alter_column('categories', 'path',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.add_column('cart_items', sa.Column('added_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True))
    op.add_column('cart_items', sa.Column('variant_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'cart_items', type_='foreignkey')
    op.create_foreign_key('cart_items_variant_id_fkey', 'cart_items', 'product_variants', ['variant_id'], ['id'])
    op.alter_column('cart_items', 'quantity',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('cart_items', 'updated_at')
    op.drop_column('cart_items', 'created_at')
    op.drop_column('cart_items', 'item_metadata')
    op.drop_column('cart_items', 'selected')
    op.drop_column('cart_items', 'item_id')
    op.add_column('buy_history', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('buy_history', sa.Column('order_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('buy_history', sa.Column('price', sa.NUMERIC(), autoincrement=False, nullable=True))
    op.add_column('buy_history', sa.Column('buy_history_id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.add_column('buy_history', sa.Column('purchase_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'buy_history', type_='foreignkey')
    op.drop_constraint(None, 'buy_history', type_='foreignkey')
    op.drop_constraint(None, 'buy_history', type_='foreignkey')
    op.create_foreign_key('buy_history_order_id_fkey', 'buy_history', 'orders', ['order_id'], ['order_id'])
    op.create_foreign_key('buy_history_customer_id_fkey', 'buy_history', 'customers', ['customer_id'], ['customer_id'])
    op.alter_column('buy_history', 'quantity',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('buy_history', 'product_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('buy_history', 'updated_at')
    op.drop_column('buy_history', 'created_at')
    op.drop_column('buy_history', 'notes')
    op.drop_column('buy_history', 'status')
    op.drop_column('buy_history', 'transaction_id')
    op.drop_column('buy_history', 'total_amount')
    op.drop_column('buy_history', 'price_at_time')
    op.drop_column('buy_history', 'user_id')
    op.drop_column('buy_history', 'history_id')
    op.alter_column('brands', 'brand_id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=False,
               autoincrement=False)
    op.create_table('order_details',
    sa.Column('order_detail_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('unit_price', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('discount', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], name='order_details_order_id_fkey'),
    sa.PrimaryKeyConstraint('order_detail_id', name='order_details_pkey')
    )
    op.create_table('fqas',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('question', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('answer', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='fqas_pkey')
    )
    op.create_index('ix_fqas_question', 'fqas', ['question'], unique=False)
    op.create_index('ix_fqas_created_at', 'fqas', ['created_at'], unique=False)
    op.create_table('product_images',
    sa.Column('product_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('base_url', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('large_url', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('medium_url', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('is_gallery', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], name='product_images_product_id_fkey'),
    sa.PrimaryKeyConstraint('product_id', 'base_url', name='product_images_pkey')
    )
    op.create_table('inventories',
    sa.Column('product_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('product_virtual_type', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('fulfillment_type', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], name='inventories_product_id_fkey'),
    sa.PrimaryKeyConstraint('product_id', name='inventories_pkey')
    )
    op.create_table('shipping_info',
    sa.Column('shipping_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('shipping_status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('estimated_delivery', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('tracking_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('carrier', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], name='shipping_info_order_id_fkey'),
    sa.PrimaryKeyConstraint('shipping_id', name='shipping_info_pkey')
    )
    op.create_table('product_variants',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('sku', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('price', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('original_price', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('inventory_status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('thumbnail_url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('option1', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='product_variants_pkey')
    )
    op.create_table('warranties',
    sa.Column('product_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('warranty_location', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('warranty_period', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('warranty_form', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('warranty_url', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('return_policy', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], name='warranties_product_id_fkey'),
    sa.PrimaryKeyConstraint('product_id', name='warranties_pkey')
    )
    op.drop_table('shipping')
    op.drop_table('promotions')
    op.drop_table('payments')
    op.drop_table('order_status')
    op.drop_table('order_items')
    op.drop_table('finance')
    op.drop_table('policies')
    op.drop_table('customer_service')
    op.drop_table('analytics')
    # ### end Alembic commands ###
