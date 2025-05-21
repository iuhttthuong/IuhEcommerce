"""create chats table

Revision ID: 39eadb05536a
Revises: init_all_tables
Create Date: 2025-05-20 23:16:59.225780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '39eadb05536a'
down_revision: Union[str, None] = 'init_all_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get connection
    connection = op.get_bind()
    
    # Drop existing tables if they exist
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Drop foreign key constraints first
            IF EXISTS (
                SELECT 1 
                FROM information_schema.table_constraints 
                WHERE constraint_name = 'chat_messages_chat_id_fkey'
            ) THEN
                ALTER TABLE chat_messages DROP CONSTRAINT chat_messages_chat_id_fkey;
            END IF;
            
            IF EXISTS (
                SELECT 1 
                FROM information_schema.table_constraints 
                WHERE constraint_name = 'chats_shop_id_fkey'
            ) THEN
                ALTER TABLE chats DROP CONSTRAINT chats_shop_id_fkey;
            END IF;
            
            IF EXISTS (
                SELECT 1 
                FROM information_schema.table_constraints 
                WHERE constraint_name = 'chats_customer_id_fkey'
            ) THEN
                ALTER TABLE chats DROP CONSTRAINT chats_customer_id_fkey;
            END IF;
            
            -- Drop the tables
            DROP TABLE IF EXISTS chat_messages CASCADE;
            DROP TABLE IF EXISTS chats CASCADE;
        END $$;
    """))
    
    # Create chats table
    op.create_table(
        'chats',
        sa.Column('chat_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('shop_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('last_message_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ),
        sa.ForeignKeyConstraint(['shop_id'], ['shops.shop_id'], ),
        sa.PrimaryKeyConstraint('chat_id')
    )

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('message_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('sender_type', sa.String(length=20), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.chat_id'], ),
        sa.PrimaryKeyConstraint('message_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('chat_messages')
    op.drop_table('chats')

