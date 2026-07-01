from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .api import models as models_router
from .api import agents as agents_router
from .api import datasets as datasets_router
from .api import evaluations as evaluations_router
from .api import leaderboard as leaderboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Code Leaderboard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models_router.router)
app.include_router(agents_router.router)
app.include_router(datasets_router.router)
app.include_router(evaluations_router.router)
app.include_router(leaderboard_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
