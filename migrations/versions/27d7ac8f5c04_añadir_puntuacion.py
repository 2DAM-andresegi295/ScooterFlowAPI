"""añadir puntuacion

Revision ID: 27d7ac8f5c04
Revises: 469d9e511fa1
Create Date: 2026-03-03 19:26:52.048089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27d7ac8f5c04'
down_revision: Union[str, Sequence[str], None] = '469d9e511fa1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('scooters', sa.Column('puntuacion_usuario', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('scooters', 'puntuacion_usuario')
