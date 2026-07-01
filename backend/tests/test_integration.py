import pytest

AUTH_HEADER = {"Authorization": "Bearer dev-token-123"}


@pytest.mark.asyncio
async def test_full_flow(client, db_session):
    # Register model
    model_resp = await client.post("/api/models", json={
        "name": "IntegModel", "model_type": "开源",
        "api_endpoint": "http://api.example.com", "model_identifier": "integ-model",
    }, headers=AUTH_HEADER)
    assert model_resp.status_code == 201
    model_id = model_resp.json()["id"]

    # Register agent
    agent_resp = await client.post("/api/agents", json={
        "name": "IntegAgent", "agent_type": "claude-code", "docker_image": "claude-code:latest",
    }, headers=AUTH_HEADER)
    assert agent_resp.status_code == 201
    agent_id = agent_resp.json()["id"]

    # Verify model and agent in list
    models = await client.get("/api/models")
    assert any(m["id"] == model_id for m in models.json()["models"])
    agents = await client.get("/api/agents")
    assert any(a["id"] == agent_id for a in agents.json()["agents"])

    # Seed dataset directly
    from app.models import Dataset
    dataset = Dataset(name="IntegDataset", language="Java", task_count=10, config_path="integ.json")
    db_session.add(dataset)
    await db_session.commit()

    # Create evaluation
    eval_resp = await client.post("/api/evaluations", json={
        "model_id": model_id, "agent_id": agent_id, "dataset_id": dataset.id,
    }, headers=AUTH_HEADER)
    assert eval_resp.status_code == 201
    task_id = eval_resp.json()["task_id"]

    # Get evaluation detail
    detail = await client.get(f"/api/evaluations/{task_id}")
    assert detail.status_code == 200
    assert detail.json()["status"] == "排队中"

    # Leaderboard should be empty (task not completed)
    lb = await client.get("/api/leaderboard")
    assert lb.status_code == 200
    # Task is queued, not completed, so not in leaderboard
    assert all(r["task_id"] != task_id for r in lb.json()["rankings"])


@pytest.mark.asyncio
async def test_leaderboard_filtering_integration(client, db_session):
    from app.models import Model, Agent, Dataset, EvaluationTask
    from datetime import datetime, timezone

    model = Model(name="FilterModel", model_type="开源", api_endpoint="http://x.com", model_identifier="fm")
    agent = Agent(name="FilterAgent", agent_type="claude-code", docker_image="img:latest")
    dataset = Dataset(name="FilterDataset", language="Java", task_count=80, config_path="f.json")
    db_session.add_all([model, agent, dataset])
    await db_session.commit()

    task = EvaluationTask(
        model_id=model.id, agent_id=agent.id, dataset_id=dataset.id,
        total_tasks=80, resolved_tasks=35, resolved_rate=43.75,
        status="已完成", created_by="tester",
        completed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db_session.add(task)
    await db_session.commit()

    resp = await client.get("/api/leaderboard?model=FilterModel&agent=FilterAgent&dataset=FilterDataset")
    assert resp.status_code == 200
    rankings = resp.json()["rankings"]
    assert len(rankings) == 1
    assert rankings[0]["resolved_rate"] == 43.75
    assert rankings[0]["task_id"] == task.id
