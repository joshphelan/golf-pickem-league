"""add_timezone_to_tournaments

Revision ID: 7d2e9f3a1b5c
Revises: 6f3858a8466c
Create Date: 2025-10-09 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d2e9f3a1b5c'
down_revision = '6f3858a8466c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add timezone column to tournaments table."""
    op.add_column('tournaments', sa.Column('timezone', sa.String(), nullable=True))
    
    # Set default timezone for existing records
    op.execute("UPDATE tournaments SET timezone = 'America/New_York' WHERE timezone IS NULL")


def downgrade() -> None:
    """Remove timezone column from tournaments table."""
    op.drop_column('tournaments', 'timezone')

