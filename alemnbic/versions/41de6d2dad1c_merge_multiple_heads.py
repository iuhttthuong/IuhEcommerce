"""merge multiple heads

Revision ID: 41de6d2dad1c
Revises: 7fc2cb62ae59
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41de6d2dad1c'
down_revision: Union[str, None] = '7fc2cb62ae59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
