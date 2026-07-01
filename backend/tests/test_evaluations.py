import pytest
from app.models import Model, Agent, Dataset, EvaluationTask, SubTaskResult

AUTH_HEADER = {"Authorization": "Bearer dev-token-123"}


async def _seed(db_session):
    model = Model(name="TestModel", model_type="开源", api_endpoint="http://x.com", model_identifier="tm")
    agent = Agent(name="TestAgent", agent_type="claude-code", docker_image="claude:latest")
    dataset = Dataset(name="TestDataset", language="Java", task_count=5, config_path="test.json")
    db_session.add_all([model, agent, dataset])
    await db_session.commit()
    return model, agent, dataset


@pytest.mark.asyncio
async def test_create_evaluation(client, db_session):
    model, agent, dataset = await _seed(db_session)
    resp = await client.post("/api/evaluations", json={
        "model_id": model.id,
        "agent_id": agent.id,
        "dataset_id": dataset.id,
    }, headers=AUTH_HEADER)
    assert resp.status_code == 201
    data = resp.json()
    assert "task_id" in data
    assert data["status"] == "排队中"
    assert data["message"] == "评测任务已创建"


@pytest.mark.asyncio
async def test_create_evaluation_no_auth(client, db_session):
    model, agent, dataset = await _seed(db_session)
    resp = await client.post("/api/evaluations", json={
        "model_id": model.id, "agent_id": agent.id, "dataset_id": dataset.id,
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_evaluation_model_not_found(client, db_session):
    _, agent, dataset = await _seed(db_session)
    resp = await client.post("/api/evaluations", json={
        "model_id": "nonexistent", "agent_id": agent.id, "dataset_id": dataset.id,
    }, headers=AUTH_HEADER)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_evaluation(client, db_session):
    model, agent, dataset = await _seed(db_session)
    create_resp = await client.post("/api/evaluations", json={
        "model_id": model.id, "agent_id": agent.id, "dataset_id": dataset.id,
    }, headers=AUTH_HEADER)
    task_id = create_resp.json()["task_id"]

    resp = await client.get(f"/api/evaluations/{task_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["task_id"] == task_id
    assert data["status"] == "排队中"
    assert data["model_name"] == "TestModel"
    assert "progress" in data


@pytest.mark.asyncio
async def test_get_evaluation_not_found(client):
    resp = await client.get("/api/evaluations/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_subtask_detail(client, db_session):
    model, agent, dataset = await _seed(db_session)
    task = EvaluationTask(
        model_id=model.id, agent_id=agent.id, dataset_id=dataset.id,
        total_tasks=5, created_by="tester", status="已完成",
        resolved_rate=60.0, resolved_tasks=3,
    )
    db_session.add(task)
    await db_session.commit()

    subtask = SubTaskResult(
        task_id=task.id,
        dataset_task_id="task-001",
        result="通过",
        trajectory={"steps": []},
        code_diff="diff --git a/Test.java b/Test.java",
        execution_time=90.0,
        token_usage=8000,
    )
    db_session.add(subtask)
    await db_session.commit()

    resp = await client.get(f"/api/evaluations/{task.id}/subtasks/{subtask.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"] == "通过"
    assert data["dataset_task_id"] == "task-001"
    assert data["execution_time"] == 90.0


@pytest.mark.asyncio
async def test_evaluation_unavailable_model(client, db_session):
    model = Model(name="UnavailModel", model_type="开源", api_endpoint="http://x.com",
                  model_identifier="um", status="不可用")
    agent = Agent(name="AgentX", agent_type="claude-code", docker_image="img:latest")
    dataset = Dataset(name="DS_X", language="Java", task_count=5, config_path="x.json")
    db_session.add_all([model, agent, dataset])
    await db_session.commit()

    resp = await client.post("/api/evaluations", json={
        "model_id": model.id, "agent_id": agent.id, "dataset_id": dataset.id,
    }, headers=AUTH_HEADER)
    assert resp.status_code == 400
