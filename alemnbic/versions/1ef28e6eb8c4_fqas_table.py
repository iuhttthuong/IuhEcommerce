"""fqas table

Revision ID: 1ef28e6eb8c4
Revises: 4e5e8c536b56
Create Date: 2025-05-10 20:34:16.536242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ef28e6eb8c4'
down_revision: Union[str, None] = '4e5e8c536b56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'fqas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_fqas_question'), 'fqas', ['question'], unique=False)
    op.create_index(op.f('ix_fqas_created_at'), 'fqas', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_fqas_created_at'), 'fqas')
    op.drop_index(op.f('ix_fqas_question'), 'fqas')
    op.drop_table('fqas')
