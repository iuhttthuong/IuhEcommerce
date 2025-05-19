"""merge multiple heads

Revision ID: 7fc2cb62ae59
Revises: 5d288a0b8f0b
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fc2cb62ae59'
down_revision: Union[str, None] = '5d288a0b8f0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
