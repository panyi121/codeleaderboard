"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-01

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "models",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("model_type", sa.Enum("开源", "闭源", name="model_type_enum"), nullable=False),
        sa.Column("api_endpoint", sa.String(512), nullable=False),
        sa.Column("model_identifier", sa.String(128), nullable=False),
        sa.Column("status", sa.Enum("可用", "不可用", name="model_status_enum"), nullable=False, server_default="可用"),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_table(
        "agents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("agent_type", sa.String(64), nullable=False),
        sa.Column("docker_image", sa.String(512), nullable=False),
        sa.Column("status", sa.Enum("可用", "不可用", name="agent_status_enum"), nullable=False, server_default="可用"),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_table(
        "datasets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("task_count", sa.Integer, nullable=False),
        sa.Column("config_path", sa.String(512), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_table(
        "evaluation_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("model_id", sa.String(36), sa.ForeignKey("models.id"), nullable=False),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("dataset_id", sa.String(36), sa.ForeignKey("datasets.id"), nullable=False),
        sa.Column("status", sa.Enum("排队中", "执行中", "已完成", "失败", name="task_status_enum"), nullable=False, server_default="排队中"),
        sa.Column("resolved_rate", sa.Float, nullable=True),
        sa.Column("total_tasks", sa.Integer, nullable=False),
        sa.Column("resolved_tasks", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("created_by", sa.String(128), nullable=False),
    )
    op.create_table(
        "subtask_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task_id", sa.String(36), sa.ForeignKey("evaluation_tasks.id"), nullable=False),
        sa.Column("dataset_task_id", sa.String(128), nullable=False),
        sa.Column("result", sa.Enum("通过", "失败", "超时", "未执行", name="subtask_result_enum"), nullable=False),
        sa.Column("trajectory", sa.JSON, nullable=True),
        sa.Column("code_diff", sa.Text, nullable=True),
        sa.Column("execution_time", sa.Float, nullable=True),
        sa.Column("token_usage", sa.Integer, nullable=True),
        sa.Column("error_log", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("subtask_results")
    op.drop_table("evaluation_tasks")
    op.drop_table("datasets")
    op.drop_table("agents")
    op.drop_table("models")
