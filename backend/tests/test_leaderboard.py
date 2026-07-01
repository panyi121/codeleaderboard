import pytest
from datetime import datetime, timezone
from app.models import Model, Agent, Dataset, EvaluationTask


async def _make_completed_task(db_session, model_name, agent_name, dataset_name, resolved_rate, resolved_tasks, total_tasks):
    model = Model(name=model_name, model_type="开源", api_endpoint="http://x.com", model_identifier=model_name.lower())
    agent = Agent(name=agent_name, agent_type="claude-code", docker_image="img:latest")
    dataset = Dataset(name=dataset_name, language="Java", task_count=total_tasks, config_path=f"{dataset_name}.json")
    db_session.add_all([model, agent, dataset])
    await db_session.commit()

    task = EvaluationTask(
        model_id=model.id, agent_id=agent.id, dataset_id=dataset.id,
        total_tasks=total_tasks, resolved_tasks=resolved_tasks, resolved_rate=resolved_rate,
        status="已完成", created_by="tester",
        completed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db_session.add(task)
    await db_session.commit()
    return task


@pytest.mark.asyncio
async def test_leaderboard_empty(client):
    resp = await client.get("/api/leaderboard")
    assert resp.status_code == 200
    assert resp.json() == {"rankings": []}


@pytest.mark.asyncio
async def test_leaderboard_sorted_by_resolved_rate(client, db_session):
    await _make_completed_task(db_session, "ModelA", "AgentA", "DatasetA", 43.75, 35, 80)
    await _make_completed_task(db_session, "ModelB", "AgentB", "DatasetB", 62.5, 50, 80)

    resp = await client.get("/api/leaderboard")
    assert resp.status_code == 200
    rankings = resp.json()["rankings"]
    assert len(rankings) == 2
    assert rankings[0]["resolved_rate"] >= rankings[1]["resolved_rate"]
    assert rankings[0]["rank"] == 1


@pytest.mark.asyncio
async def test_leaderboard_filter_by_model(client, db_session):
    await _make_completed_task(db_session, "GLM-5.2", "AgentF1", "DSF1", 50.0, 40, 80)
    await _make_completed_task(db_session, "DeepSeek", "AgentF2", "DSF2", 30.0, 24, 80)

    resp = await client.get("/api/leaderboard?model=GLM-5.2")
    assert resp.status_code == 200
    rankings = resp.json()["rankings"]
    assert len(rankings) == 1
    assert rankings[0]["model_name"] == "GLM-5.2"


@pytest.mark.asyncio
async def test_leaderboard_filter_by_agent(client, db_session):
    await _make_completed_task(db_session, "ModelG1", "Claude Code", "DSG1", 55.0, 44, 80)
    await _make_completed_task(db_session, "ModelG2", "OpenCode", "DSG2", 40.0, 32, 80)

    resp = await client.get("/api/leaderboard?agent=Claude Code")
    rankings = resp.json()["rankings"]
    assert len(rankings) == 1
    assert rankings[0]["agent_name"] == "Claude Code"


@pytest.mark.asyncio
async def test_leaderboard_filter_by_dataset(client, db_session):
    await _make_completed_task(db_session, "ModelH1", "AgentH1", "Multi-SWE-Bench-Java", 45.0, 36, 80)
    await _make_completed_task(db_session, "ModelH2", "AgentH2", "OtherDataset", 50.0, 40, 80)

    resp = await client.get("/api/leaderboard?dataset=Multi-SWE-Bench-Java")
    rankings = resp.json()["rankings"]
    assert len(rankings) == 1
    assert rankings[0]["dataset_name"] == "Multi-SWE-Bench-Java"
