"""document stored file for downloads

Revision ID: 0002_document_stored_file
Revises: 0001_initial_schema
Create Date: 2026-04-10
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_document_stored_file"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("stored_file_path", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "stored_file_path")
