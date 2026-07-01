from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Model
from ..schemas import ModelCreate, ModelResponse
from .auth import verify_token

router = APIRouter(prefix="/api/models", tags=["models"])


@router.post("", response_model=ModelResponse, status_code=201)
async def register_model(
    data: ModelCreate,
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    existing = await db.execute(select(Model).where(Model.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="模型名称已存在")

    if data.model_type not in ("开源", "闭源"):
        raise HTTPException(status_code=422, detail="model_type 必须为 开源 或 闭源")

    model = Model(
        name=data.name,
        model_type=data.model_type,
        api_endpoint=data.api_endpoint,
        model_identifier=data.model_identifier,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model


@router.get("", response_model=dict)
async def list_models(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Model).order_by(Model.created_at.desc()))
    models = result.scalars().all()
    return {"models": [ModelResponse.model_validate(m) for m in models]}
