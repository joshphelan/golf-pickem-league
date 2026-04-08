"""raise default max_members from 10 to 50 for existing leagues

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-08

Updates all existing leagues that still have the original default of 10
to the new default of 50, so they are no longer artificially capped.

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE leagues SET max_members = 50 WHERE max_members = 10")


def downgrade() -> None:
    op.execute("UPDATE leagues SET max_members = 10 WHERE max_members = 50")
