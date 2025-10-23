"""add refresh timestamps to tournaments

Revision ID: b54210a21586
Revises: 7d2e9f3a1b5c
Create Date: 2025-10-22 20:36:58.829189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b54210a21586'
down_revision = '7d2e9f3a1b5c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add refresh timestamp columns to tournaments table
    op.add_column('tournaments', sa.Column('last_schedule_refresh', sa.DateTime(), nullable=True))
    op.add_column('tournaments', sa.Column('last_player_refresh', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove refresh timestamp columns
    op.drop_column('tournaments', 'last_player_refresh')
    op.drop_column('tournaments', 'last_schedule_refresh')

