"""add scoring_count to leagues and league_comments table

Revision ID: a1b2c3d4e5f6
Revises: c8f3a2d1e5b7
Create Date: 2026-04-02

Adds:
- scoring_count column to leagues (nullable int; NULL = count all players)
- league_comments table for per-league chat

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'c8f3a2d1e5b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add scoring_count to leagues
    op.add_column('leagues', sa.Column('scoring_count', sa.Integer(), nullable=True))

    # Create league_comments table
    op.create_table(
        'league_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('league_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('leagues.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.String(1000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_league_comments_league_id', 'league_comments', ['league_id'])


def downgrade() -> None:
    op.drop_index('ix_league_comments_league_id', table_name='league_comments')
    op.drop_table('league_comments')
    op.drop_column('leagues', 'scoring_count')
