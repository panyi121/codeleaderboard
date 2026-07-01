from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Any


# Model schemas
class ModelCreate(BaseModel):
    name: str
    model_type: str  # 开源 / 闭源
    api_endpoint: str
    model_identifier: str


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    model_type: str
    api_endpoint: str
    model_identifier: str
    status: str
    created_at: datetime


# Agent schemas
class AgentCreate(BaseModel):
    name: str
    agent_type: str
    docker_image: str


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    agent_type: str
    docker_image: str
    status: str
    created_at: datetime


# Dataset schemas
class DatasetCreate(BaseModel):
    name: str
    language: str
    task_count: int
    config_path: str
    description: Optional[str] = None


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    language: str
    task_count: int
    description: Optional[str]
    created_at: datetime


class DatasetTask(BaseModel):
    task_id: str
    repository: str
    issue_title: str
    difficulty: str


# EvaluationTask schemas
class EvaluationCreate(BaseModel):
    model_id: str
    agent_id: str
    dataset_id: str


class SubTaskResultBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    dataset_task_id: str
    result: str
    execution_time: Optional[float]
    token_usage: Optional[int]


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    task_id: str
    model_name: str
    agent_name: str
    dataset_name: str
    status: str
    progress: str
    resolved_rate: Optional[float]
    subtask_results: List[SubTaskResultBrief]
    created_at: datetime
    completed_at: Optional[datetime]


class EvaluationCreateResponse(BaseModel):
    task_id: str
    status: str
    message: str


# SubTaskResult schemas
class SubTaskResultDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    dataset_task_id: str
    result: str
    trajectory: Optional[Any]
    code_diff: Optional[str]
    execution_time: Optional[float]
    token_usage: Optional[int]
    error_log: Optional[str]


# Leaderboard schemas
class LeaderboardEntry(BaseModel):
    rank: int
    model_name: str
    agent_name: str
    dataset_name: str
    resolved_rate: float
    total_tasks: int
    resolved_tasks: int
    task_id: str


class LeaderboardResponse(BaseModel):
    rankings: List[LeaderboardEntry]
