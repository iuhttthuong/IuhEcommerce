"""merge multiple heads

Revision ID: 4af4e079be35
Revises: 41de6d2dad1c, add_shop_and_chat_fields
Create Date: 2025-05-17 12:54:13.165613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4af4e079be35'
down_revision: Union[str, None] = ('41de6d2dad1c', 'add_shop_and_chat_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
