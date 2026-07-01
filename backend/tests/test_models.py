import pytest
from sqlalchemy import select
from app.models import Model, Agent, Dataset, EvaluationTask, SubTaskResult


@pytest.mark.asyncio
async def test_create_model(db_session):
    model = Model(name="GLM-5.2", model_type="开源", api_endpoint="http://api.example.com", model_identifier="glm-5.2")
    db_session.add(model)
    await db_session.commit()

    result = await db_session.execute(select(Model).where(Model.name == "GLM-5.2"))
    found = result.scalar_one_or_none()
    assert found is not None
    assert found.name == "GLM-5.2"
    assert found.status == "可用"


@pytest.mark.asyncio
async def test_create_agent(db_session):
    agent = Agent(name="Claude Code", agent_type="claude-code", docker_image="claude-code:latest")
    db_session.add(agent)
    await db_session.commit()

    result = await db_session.execute(select(Agent).where(Agent.name == "Claude Code"))
    found = result.scalar_one_or_none()
    assert found is not None
    assert found.status == "可用"


@pytest.mark.asyncio
async def test_create_dataset(db_session):
    ds = Dataset(name="Multi-SWE-Bench-Java", language="Java", task_count=80, config_path="java.json")
    db_session.add(ds)
    await db_session.commit()

    result = await db_session.execute(select(Dataset).where(Dataset.name == "Multi-SWE-Bench-Java"))
    found = result.scalar_one_or_none()
    assert found is not None
    assert found.task_count == 80


@pytest.mark.asyncio
async def test_create_evaluation_task(db_session):
    model = Model(name="M1", model_type="开源", api_endpoint="http://x.com", model_identifier="m1")
    agent = Agent(name="A1", agent_type="claude-code", docker_image="img:latest")
    dataset = Dataset(name="D1", language="Java", task_count=10, config_path="d1.json")
    db_session.add_all([model, agent, dataset])
    await db_session.commit()

    task = EvaluationTask(
        model_id=model.id,
        agent_id=agent.id,
        dataset_id=dataset.id,
        total_tasks=10,
        created_by="test-token",
    )
    db_session.add(task)
    await db_session.commit()

    result = await db_session.execute(select(EvaluationTask).where(EvaluationTask.id == task.id))
    found = result.scalar_one_or_none()
    assert found is not None
    assert found.status == "排队中"
    assert found.resolved_tasks == 0


@pytest.mark.asyncio
async def test_create_subtask_result(db_session):
    model = Model(name="M2", model_type="闭源", api_endpoint="http://x.com", model_identifier="m2")
    agent = Agent(name="A2", agent_type="opencode", docker_image="opencode:latest")
    dataset = Dataset(name="D2", language="Python", task_count=5, config_path="d2.json")
    db_session.add_all([model, agent, dataset])
    await db_session.commit()

    task = EvaluationTask(
        model_id=model.id, agent_id=agent.id, dataset_id=dataset.id,
        total_tasks=5, created_by="tester"
    )
    db_session.add(task)
    await db_session.commit()

    subtask = SubTaskResult(
        task_id=task.id,
        dataset_task_id="task-001",
        result="通过",
        execution_time=120.5,
        token_usage=15000,
    )
    db_session.add(subtask)
    await db_session.commit()

    result = await db_session.execute(select(SubTaskResult).where(SubTaskResult.task_id == task.id))
    found = result.scalar_one_or_none()
    assert found is not None
    assert found.result == "通过"
    assert found.execution_time == 120.5


@pytest.mark.asyncio
async def test_model_unique_constraint(db_session):
    from sqlalchemy.exc import IntegrityError
    m1 = Model(name="UniqueModel", model_type="开源", api_endpoint="http://x.com", model_identifier="um")
    m2 = Model(name="UniqueModel", model_type="闭源", api_endpoint="http://y.com", model_identifier="um2")
    db_session.add(m1)
    await db_session.commit()
    db_session.add(m2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
