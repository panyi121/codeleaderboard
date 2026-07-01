from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models import EvaluationTask, SubTaskResult, Model, Agent, Dataset
from ..schemas import (
    EvaluationCreate, EvaluationCreateResponse,
    EvaluationResponse, SubTaskResultBrief, SubTaskResultDetail
)
from .auth import verify_token

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


@router.post("", response_model=EvaluationCreateResponse, status_code=201)
async def create_evaluation(
    data: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token),
):
    model_row = await db.get(Model, data.model_id)
    if not model_row:
        raise HTTPException(status_code=404, detail="模型不存在")
    if model_row.status != "可用":
        raise HTTPException(status_code=400, detail="模型状态不可用")

    agent_row = await db.get(Agent, data.agent_id)
    if not agent_row:
        raise HTTPException(status_code=404, detail="Agent不存在")
    if agent_row.status != "可用":
        raise HTTPException(status_code=400, detail="Agent状态不可用")

    dataset_row = await db.get(Dataset, data.dataset_id)
    if not dataset_row:
        raise HTTPException(status_code=404, detail="数据集不存在")

    task = EvaluationTask(
        model_id=data.model_id,
        agent_id=data.agent_id,
        dataset_id=data.dataset_id,
        total_tasks=dataset_row.task_count,
        created_by=token,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Dispatch Celery task (import here to avoid circular imports)
    try:
        from ..workers import run_evaluation
        run_evaluation.delay(task.id)
    except Exception:
        pass  # If Celery/Redis not available, task stays queued

    return EvaluationCreateResponse(
        task_id=task.id,
        status=task.status,
        message="评测任务已创建",
    )


@router.get("/{task_id}", response_model=EvaluationResponse)
async def get_evaluation(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EvaluationTask)
        .options(
            selectinload(EvaluationTask.model),
            selectinload(EvaluationTask.agent),
            selectinload(EvaluationTask.dataset),
            selectinload(EvaluationTask.subtask_results),
        )
        .where(EvaluationTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="评测任务不存在")

    completed = sum(
        1 for sr in task.subtask_results
        if sr.result in ("通过", "失败", "超时")
    )

    return EvaluationResponse(
        task_id=task.id,
        model_name=task.model.name,
        agent_name=task.agent.name,
        dataset_name=task.dataset.name,
        status=task.status,
        progress=f"{completed}/{task.total_tasks}",
        resolved_rate=task.resolved_rate,
        subtask_results=[
            SubTaskResultBrief(
                id=sr.id,
                dataset_task_id=sr.dataset_task_id,
                result=sr.result,
                execution_time=sr.execution_time,
                token_usage=sr.token_usage,
            )
            for sr in task.subtask_results
        ],
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


@router.get("/{task_id}/subtasks/{subtask_id}", response_model=SubTaskResultDetail)
async def get_subtask_detail(task_id: str, subtask_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SubTaskResult).where(
            SubTaskResult.id == subtask_id,
            SubTaskResult.task_id == task_id,
        )
    )
    subtask = result.scalar_one_or_none()
    if not subtask:
        raise HTTPException(status_code=404, detail="子任务不存在")

    return SubTaskResultDetail(
        dataset_task_id=subtask.dataset_task_id,
        result=subtask.result,
        trajectory=subtask.trajectory,
        code_diff=subtask.code_diff,
        execution_time=subtask.execution_time,
        token_usage=subtask.token_usage,
        error_log=subtask.error_log,
    )
