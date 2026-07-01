import asyncio
from celery import Celery
from .config import settings

celery_app = Celery("codeleaderboard", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=settings.max_concurrent_evaluations,
)


@celery_app.task(name="run_evaluation", bind=True, max_retries=0)
def run_evaluation(self, task_id: str) -> None:
    asyncio.run(_run_evaluation_async(task_id))


async def _run_evaluation_async(task_id: str) -> None:
    from .database import AsyncSessionLocal
    from .models import EvaluationTask
    from .services.evaluator import EvaluationRunner
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(EvaluationTask)
            .where(EvaluationTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task is None:
            return
        # Eagerly load relationships
        await db.refresh(task, ["model", "agent", "dataset", "subtask_results"])
        runner = EvaluationRunner(db)
        await runner.run(task)
