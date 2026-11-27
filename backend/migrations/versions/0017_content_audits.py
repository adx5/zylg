"""内容审核记录表 content_audits

Revision ID: 0017
Revises: 0016
Create Date: 2026-11-27

上架时触发 AI 语义审核：
  · pass    → 直接上架
  · blocked → 拒绝上架并返回原因，同时写入本表进入审核员后台
  · 审核员放行后 resolved=True，并可覆盖岗位 risk_status=pass
"""
import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_audits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("biz_type", sa.String(length=20), nullable=False),
        sa.Column("biz_id", sa.Integer(), nullable=False),
        sa.Column("city_id", sa.String(length=10), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("decision", sa.String(length=20), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=True),
        sa.Column("model", sa.String(length=50), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=True),
        sa.Column("resolved_by", sa.Integer(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_audits_id", "content_audits", ["id"])
    op.create_index("ix_content_audits_biz_type", "content_audits", ["biz_type"])
    op.create_index("ix_content_audits_biz_id", "content_audits", ["biz_id"])
    op.create_index("ix_content_audits_city_id", "content_audits", ["city_id"])
    op.create_index("ix_content_audits_decision", "content_audits", ["decision"])
    op.create_index("ix_content_audits_resolved", "content_audits", ["resolved"])


def downgrade() -> None:
    for idx in ("resolved", "decision", "city_id", "biz_id", "biz_type", "id"):
        op.drop_index(f"ix_content_audits_{idx}", table_name="content_audits")
    op.drop_table("content_audits")
