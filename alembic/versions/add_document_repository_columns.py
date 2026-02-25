"""Add columns to documents for repository (document_type, user_id, etc.)

Revision ID: a1b2c3d4e5f6
Revises: 82e96fc4f1d4
Create Date: 2025-02-23

Unifica uso del modelo Document: columnas opcionales para tipo, usuario,
organización, revisión y procesamiento.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "82e96fc4f1d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("document_type", sa.String(50), nullable=True))
    op.add_column("documents", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("processed_at", sa.DateTime(), nullable=True))
    op.add_column("documents", sa.Column("review_notes", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("reviewed_by", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("reviewed_at", sa.DateTime(), nullable=True))
    op.add_column("documents", sa.Column("processing_time_seconds", sa.Float(), nullable=True))
    op.create_index("ix_documents_document_type", "documents", ["document_type"], unique=False)
    op.create_index("ix_documents_user_id", "documents", ["user_id"], unique=False)
    op.create_index("ix_documents_organization_id", "documents", ["organization_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_documents_organization_id", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_index("ix_documents_document_type", table_name="documents")
    op.drop_column("documents", "processing_time_seconds")
    op.drop_column("documents", "reviewed_at")
    op.drop_column("documents", "reviewed_by")
    op.drop_column("documents", "review_notes")
    op.drop_column("documents", "processed_at")
    op.drop_column("documents", "organization_id")
    op.drop_column("documents", "user_id")
    op.drop_column("documents", "document_type")
