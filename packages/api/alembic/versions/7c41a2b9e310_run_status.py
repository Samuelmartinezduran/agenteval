"""eval_runs: status, error y finished_at (ejecución en background)

Revision ID: 7c41a2b9e310
Revises: 286ffa91dbf7
Create Date: 2026-07-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7c41a2b9e310'
down_revision: Union[str, None] = '286ffa91dbf7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Los runs históricos ya terminaron: server_default="completed".
    op.add_column(
        'eval_runs',
        sa.Column('status', sa.String(length=20), nullable=False, server_default='completed'),
    )
    op.add_column('eval_runs', sa.Column('error', sa.Text(), nullable=True))
    op.add_column('eval_runs', sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('eval_runs', 'finished_at')
    op.drop_column('eval_runs', 'error')
    op.drop_column('eval_runs', 'status')
