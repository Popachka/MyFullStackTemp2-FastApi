"""add telegram id to user

Revision ID: 2d9f6c1b4d8f
Revises: 14e8ee05cb24
Create Date: 2025-12-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2d9f6c1b4d8f"
down_revision = "14e8ee05cb24"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("telegram_id", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_user_telegram_id"),
        "user",
        ["telegram_id"],
        unique=True,
    )


def downgrade():
    op.drop_index(op.f("ix_user_telegram_id"), table_name="user")
    op.drop_column("user", "telegram_id")

