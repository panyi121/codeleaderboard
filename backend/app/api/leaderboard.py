from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from ..database import get_db
from ..models import EvaluationTask, Model, Agent, Dataset
from ..schemas import LeaderboardResponse, LeaderboardEntry

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    model: Optional[str] = Query(None),
    agent: Optional[str] = Query(None),
    dataset: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(EvaluationTask)
        .options(
            selectinload(EvaluationTask.model),
            selectinload(EvaluationTask.agent),
            selectinload(EvaluationTask.dataset),
        )
        .where(EvaluationTask.status == "已完成")
        .order_by(EvaluationTask.completed_at.desc())
    )
    result = await db.execute(stmt)
    all_tasks = result.scalars().all()

    # Filter by query params
    if model:
        all_tasks = [t for t in all_tasks if t.model.name == model]
    if agent:
        all_tasks = [t for t in all_tasks if t.agent.name == agent]
    if dataset:
        all_tasks = [t for t in all_tasks if t.dataset.name == dataset]

    # Keep only the latest per (model, agent, dataset) combination
    seen = {}
    for task in all_tasks:
        key = (task.model_id, task.agent_id, task.dataset_id)
        if key not in seen:
            seen[key] = task

    # Sort by resolved_rate descending
    sorted_tasks = sorted(seen.values(), key=lambda t: t.resolved_rate or 0.0, reverse=True)

    rankings = [
        LeaderboardEntry(
            rank=idx + 1,
            model_name=t.model.name,
            agent_name=t.agent.name,
            dataset_name=t.dataset.name,
            resolved_rate=t.resolved_rate or 0.0,
            total_tasks=t.total_tasks,
            resolved_tasks=t.resolved_tasks,
            task_id=t.id,
        )
        for idx, t in enumerate(sorted_tasks)
    ]

    return LeaderboardResponse(rankings=rankings)
