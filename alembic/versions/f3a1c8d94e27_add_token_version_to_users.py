"""add token_version to users

Revision ID: f3a1c8d94e27
Revises: dc876ced1c2e
Create Date: 2026-10-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f3a1c8d94e27'
down_revision: Union[str, Sequence[str], None] = 'dc876ced1c2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('token_version', sa.Integer(), nullable=False, server_default=sa.text('0')),
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'token_version')