"""store photo bytes in db

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-29 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("photos", "filename")
    op.add_column("photos", sa.Column("data", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("photos", "data")
    op.add_column(
        "photos",
        sa.Column("filename", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
    )
