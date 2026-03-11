"""add catalog fields and subscriptions table

Revision ID: 7d725c48738d
Revises: 6708804885d7
Create Date: 2026-03-11 22:45:55.031681

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7d725c48738d"
down_revision: str | Sequence[str] | None = "6708804885d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add catalog fields to sources, create subscriptions table, migrate data."""
    # 1. Add catalog fields to sources table
    with op.batch_alter_table("sources") as batch_op:
        batch_op.add_column(sa.Column("geographic_level", sa.String(20), nullable=True))
        batch_op.add_column(sa.Column("country_code", sa.String(2), nullable=True))
        batch_op.add_column(sa.Column("region", sa.String(100), nullable=True))
        batch_op.add_column(sa.Column("tags", sa.JSON(), server_default="[]"))
        batch_op.add_column(
            sa.Column("is_curated", sa.Boolean(), server_default=sa.text("0"))
        )
        batch_op.add_column(sa.Column("verified_at", sa.DateTime(), nullable=True))

    # 2. Create subscriptions table (IF NOT EXISTS for safety — init_db may have
    #    already created it via Base.metadata.create_all)
    op.execute(
        "CREATE TABLE IF NOT EXISTS subscriptions ("
        "  id INTEGER NOT NULL PRIMARY KEY,"
        "  user_id INTEGER NOT NULL DEFAULT 1,"
        "  source_id INTEGER NOT NULL,"
        "  is_active BOOLEAN DEFAULT 1,"
        "  update_frequency_override INTEGER,"
        "  added_at DATETIME,"
        "  FOREIGN KEY(source_id) REFERENCES sources(id),"
        "  UNIQUE(user_id, source_id)"
        ")"
    )
    # Create indexes only if they don't exist (SQLite supports IF NOT EXISTS)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_subscriptions_id ON subscriptions(id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_subscriptions_user_id ON subscriptions(user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_subscriptions_source_id ON subscriptions(source_id)"
    )

    # 3. Data migration: create a subscription for each existing active source.
    # Previously all active sources were polled; now only subscribed ones are.
    # Skip sources that already have a subscription (idempotent).
    op.execute(
        "INSERT OR IGNORE INTO subscriptions (user_id, source_id, is_active, added_at) "
        "SELECT 1, id, 1, CURRENT_TIMESTAMP FROM sources WHERE is_active = 1"
    )


def downgrade() -> None:
    """Remove subscriptions table and catalog fields from sources."""
    op.drop_table("subscriptions")

    with op.batch_alter_table("sources") as batch_op:
        batch_op.drop_column("verified_at")
        batch_op.drop_column("is_curated")
        batch_op.drop_column("tags")
        batch_op.drop_column("region")
        batch_op.drop_column("country_code")
        batch_op.drop_column("geographic_level")
