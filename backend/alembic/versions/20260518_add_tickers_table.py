"""add tickers table

Revision ID: 20260518_add_tickers
Revises: 89ae883a069e
Create Date: 2026-05-18 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260518_add_tickers'
down_revision: Union[str, Sequence[str], None] = '89ae883a069e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tickers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('sector', sa.String(length=100), nullable=True),
    sa.Column('exchange', sa.String(length=50), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tickers_symbol'), 'tickers', ['symbol'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tickers_symbol'), table_name='tickers')
    op.drop_table('tickers')
