import json
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Dataset
from ..schemas import DatasetResponse, DatasetTask
from ..config import settings

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("", response_model=dict)
async def list_datasets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dataset).order_by(Dataset.created_at.desc()))
    datasets = result.scalars().all()
    return {"datasets": [DatasetResponse.model_validate(d) for d in datasets]}


@router.get("/{dataset_id}/tasks", response_model=dict)
async def list_dataset_tasks(dataset_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")

    config_path = dataset.config_path
    if not os.path.isabs(config_path):
        config_path = os.path.join(settings.datasets_config_path, config_path)

    tasks = []
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            tasks = data.get("tasks", [])
        except Exception:
            tasks = []

    return {"tasks": tasks}
