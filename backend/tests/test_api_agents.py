import pytest

AUTH_HEADER = {"Authorization": "Bearer dev-token-123"}


@pytest.mark.asyncio
async def test_register_agent(client):
    resp = await client.post("/api/agents", json={
        "name": "Claude Code",
        "agent_type": "claude-code",
        "docker_image": "claude-code:latest",
    }, headers=AUTH_HEADER)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Claude Code"
    assert data["status"] == "可用"


@pytest.mark.asyncio
async def test_register_agent_duplicate(client):
    payload = {"name": "DupAgent", "agent_type": "opencode", "docker_image": "opencode:latest"}
    await client.post("/api/agents", json=payload, headers=AUTH_HEADER)
    resp = await client.post("/api/agents", json=payload, headers=AUTH_HEADER)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_agents(client):
    await client.post("/api/agents", json={
        "name": "OpenCode", "agent_type": "opencode", "docker_image": "opencode:latest"
    }, headers=AUTH_HEADER)
    resp = await client.get("/api/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert "agents" in data
    assert len(data["agents"]) >= 1


@pytest.mark.asyncio
async def test_register_agent_no_auth(client):
    resp = await client.post("/api/agents", json={
        "name": "NoAuthAgent", "agent_type": "codex", "docker_image": "codex:latest"
    })
    assert resp.status_code in (401, 403)
