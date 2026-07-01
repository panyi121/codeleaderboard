import pytest
from app.models import Dataset

AUTH_HEADER = {"Authorization": "Bearer dev-token-123"}


@pytest.mark.asyncio
async def test_list_datasets_empty(client):
    resp = await client.get("/api/datasets")
    assert resp.status_code == 200
    assert resp.json() == {"datasets": []}


@pytest.mark.asyncio
async def test_list_datasets(client, db_session):
    ds = Dataset(name="Multi-SWE-Bench-Java", language="Java", task_count=80, config_path="java.json")
    db_session.add(ds)
    await db_session.commit()

    resp = await client.get("/api/datasets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["datasets"]) == 1
    assert data["datasets"][0]["name"] == "Multi-SWE-Bench-Java"


@pytest.mark.asyncio
async def test_list_dataset_tasks_not_found(client):
    resp = await client.get("/api/datasets/nonexistent-id/tasks")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_dataset_tasks_no_config(client, db_session):
    ds = Dataset(name="NoConfig", language="Java", task_count=5, config_path="nonexistent.json")
    db_session.add(ds)
    await db_session.commit()

    resp = await client.get(f"/api/datasets/{ds.id}/tasks")
    assert resp.status_code == 200
    assert resp.json() == {"tasks": []}
