"""add contest_state if missing

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-29 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'contest_state'"
        )
    ).scalar()

    if not exists:
        op.create_table(
            "contest_state",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("phase", sa.String(20), nullable=False, server_default="upload"),
            sa.Column("started_at", sa.DateTime(timezone=True)),
            sa.Column("finished_at", sa.DateTime(timezone=True)),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.CheckConstraint("id = 1", name="singleton"),
        )
        op.execute("INSERT INTO contest_state (id, phase) VALUES (1, 'upload')")


def downgrade() -> None:
    op.drop_table("contest_state")
