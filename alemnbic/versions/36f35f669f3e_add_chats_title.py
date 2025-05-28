"""add chats title

Revision ID: 36f35f669f3e
Revises: a9831cc188e7
Create Date: 2025-05-27 16:46:55.901066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36f35f669f3e'
down_revision: Union[str, None] = 'a9831cc188e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("chats", sa.Column("titles", sa.String(255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
