"""add shop and chat fields

Revision ID: add_shop_and_chat_fields
Revises: 
Create Date: 2024-03-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_shop_and_chat_fields'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to chat table if they do not exist
    with op.batch_alter_table('chat') as batch_op:
        batch_op.add_column(sa.Column('shop_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('role', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('context', sa.String(), nullable=True))

    # Make user_id nullable
    op.alter_column('chat', 'user_id',
        existing_type=sa.Integer(),
        nullable=True
    )


def downgrade() -> None:
    # Remove new columns from chat table
    op.drop_column('chat', 'context')
    op.drop_column('chat', 'role')
    op.drop_column('chat', 'shop_id')
    
    # Make user_id non-nullable again
    op.alter_column('chat', 'user_id',
        existing_type=sa.Integer(),
        nullable=False
    ) 