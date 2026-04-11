"""document original file type (pdf/txt)

Revision ID: 0003_document_file_type
Revises: 0002_document_stored_file
Create Date: 2026-04-11
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_document_file_type"
down_revision = "0002_document_stored_file"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("file_type", sa.String(length=16), nullable=True),
    )
    # Best-effort backfill from original filename (uploads before this column existed)
    op.execute(
        "UPDATE documents SET file_type = 'pdf' "
        "WHERE file_type IS NULL AND file_name IS NOT NULL AND LOWER(file_name) LIKE '%.pdf'"
    )
    op.execute(
        "UPDATE documents SET file_type = 'txt' "
        "WHERE file_type IS NULL AND file_name IS NOT NULL AND LOWER(file_name) LIKE '%.txt'"
    )


def downgrade() -> None:
    op.drop_column("documents", "file_type")
