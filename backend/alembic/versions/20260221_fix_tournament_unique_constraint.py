"""fix tournament unique constraint for multi-year

Revision ID: c8f3a2d1e5b7
Revises: b54210a21586
Create Date: 2026-02-21

The tourn_id column was unique globally, preventing the same tournament
(e.g., Grant Thornton) from being imported for multiple years. This migration
changes the constraint to be unique per (tourn_id, year) combination.

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8f3a2d1e5b7'
down_revision = 'b54210a21586'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Find and drop any unique constraint on tourn_id alone
    result = conn.execute(sa.text("""
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        WHERE rel.relname = 'tournaments'
        AND con.contype = 'u'
    """))

    for row in result:
        constraint_name = row[0]
        # Drop constraints that are on tourn_id alone (not our new composite one)
        if constraint_name != 'unique_tournament_per_year':
            try:
                op.drop_constraint(constraint_name, 'tournaments', type_='unique')
            except Exception:
                pass  # Constraint might already be gone

    # Drop any unique index on tourn_id (might exist instead of constraint)
    try:
        op.drop_index('ix_tournaments_tourn_id', table_name='tournaments')
    except Exception:
        pass  # Index might not exist or have different name

    # Create the new composite unique constraint (if it doesn't exist)
    try:
        op.create_unique_constraint(
            'unique_tournament_per_year',
            'tournaments',
            ['tourn_id', 'year']
        )
    except Exception:
        pass  # Might already exist


def downgrade() -> None:
    op.drop_constraint('unique_tournament_per_year', 'tournaments', type_='unique')
    op.create_unique_constraint('tournaments_tourn_id_key', 'tournaments', ['tourn_id'])
