"""modify shops table

Revision ID: modify_shops_table
Revises: add_shop_and_chat_fields
Create Date: 2024-03-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'modify_shops_table'
down_revision: Union[str, None] = 'add_shop_and_chat_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing shops table
    op.drop_table('shops')
    
    # Create new shops table with updated structure
    op.create_table('shops',
        sa.Column('shop_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('shop_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('rating', sa.DECIMAL(3,2), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('shop_id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )


def downgrade() -> None:
    # Drop new shops table
    op.drop_table('shops')
    
    # Recreate original shops table
    op.create_table('shops',
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('mail', sa.String(length=100), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.seller_id'], ),
        sa.PrimaryKeyConstraint('seller_id'),
        sa.UniqueConstraint('mail'),
        sa.UniqueConstraint('username')
    ) 