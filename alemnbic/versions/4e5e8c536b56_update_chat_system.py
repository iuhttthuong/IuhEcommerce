"""update chat system

Revision ID: 4e5e8c536b56
Revises: d041d342e6f2
Create Date: 2025-05-07 01:37:19.390090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e5e8c536b56'
down_revision: Union[str, None] = 'd041d342e6f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("customers.customer_id"), nullable=False),
        sa.Column("session_id", sa.Integer, nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chat_message",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("chat_id", sa.Integer, sa.ForeignKey("chat.id"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

        

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("chat_message")
    op.drop_table("chat")
