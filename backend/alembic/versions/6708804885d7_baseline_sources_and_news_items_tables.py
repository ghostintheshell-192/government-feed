"""baseline: sources and news_items tables

Revision ID: 6708804885d7
Revises:
Create Date: 2026-02-07 21:25:28.772223

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6708804885d7"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create sources and news_items tables."""
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("feed_url", sa.String(length=500), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("update_frequency_minutes", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("last_fetched", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sources_id"), "sources", ["id"], unique=False)

    op.create_table(
        "news_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("verification_status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_news_items_id"), "news_items", ["id"], unique=False)
    op.create_index(op.f("ix_news_items_source_id"), "news_items", ["source_id"], unique=False)
    op.create_index(
        op.f("ix_news_items_published_at"), "news_items", ["published_at"], unique=False
    )
    op.create_index(
        op.f("ix_news_items_content_hash"), "news_items", ["content_hash"], unique=True
    )


def downgrade() -> None:
    """Drop sources and news_items tables."""
    op.drop_index(op.f("ix_news_items_content_hash"), table_name="news_items")
    op.drop_index(op.f("ix_news_items_published_at"), table_name="news_items")
    op.drop_index(op.f("ix_news_items_source_id"), table_name="news_items")
    op.drop_index(op.f("ix_news_items_id"), table_name="news_items")
    op.drop_table("news_items")
    op.drop_index(op.f("ix_sources_id"), table_name="sources")
    op.drop_table("sources")
