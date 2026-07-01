import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Model(Base):
    __tablename__ = "models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    model_type: Mapped[str] = mapped_column(SAEnum("开源", "闭源", name="model_type_enum"), nullable=False)
    api_endpoint: Mapped[str] = mapped_column(String(512), nullable=False)
    model_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(SAEnum("可用", "不可用", name="model_status_enum"), nullable=False, default="可用")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    evaluations: Mapped[list["EvaluationTask"]] = relationship("EvaluationTask", back_populates="model")


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    agent_type: Mapped[str] = mapped_column(String(64), nullable=False)
    docker_image: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(SAEnum("可用", "不可用", name="agent_status_enum"), nullable=False, default="可用")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    evaluations: Mapped[list["EvaluationTask"]] = relationship("EvaluationTask", back_populates="agent")


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    task_count: Mapped[int] = mapped_column(Integer, nullable=False)
    config_path: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    evaluations: Mapped[list["EvaluationTask"]] = relationship("EvaluationTask", back_populates="dataset")


class EvaluationTask(Base):
    __tablename__ = "evaluation_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id: Mapped[str] = mapped_column(String(36), ForeignKey("models.id"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"), nullable=False)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("排队中", "执行中", "已完成", "失败", name="task_status_enum"),
        nullable=False, default="排队中"
    )
    resolved_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_tasks: Mapped[int] = mapped_column(Integer, nullable=False)
    resolved_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)

    model: Mapped["Model"] = relationship("Model", back_populates="evaluations")
    agent: Mapped["Agent"] = relationship("Agent", back_populates="evaluations")
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="evaluations")
    subtask_results: Mapped[list["SubTaskResult"]] = relationship("SubTaskResult", back_populates="task")


class SubTaskResult(Base):
    __tablename__ = "subtask_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("evaluation_tasks.id"), nullable=False)
    dataset_task_id: Mapped[str] = mapped_column(String(128), nullable=False)
    result: Mapped[str] = mapped_column(
        SAEnum("通过", "失败", "超时", "未执行", name="subtask_result_enum"),
        nullable=False
    )
    trajectory: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    code_diff: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    token_usage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_log: Mapped[str | None] = mapped_column(Text, nullable=True)

    task: Mapped["EvaluationTask"] = relationship("EvaluationTask", back_populates="subtask_results")
