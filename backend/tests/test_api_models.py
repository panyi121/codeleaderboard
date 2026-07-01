import pytest

AUTH_HEADER = {"Authorization": "Bearer dev-token-123"}


@pytest.mark.asyncio
async def test_register_model(client):
    resp = await client.post("/api/models", json={
        "name": "GLM-5.2",
        "model_type": "开源",
        "api_endpoint": "http://api.example.com",
        "model_identifier": "glm-5.2",
    }, headers=AUTH_HEADER)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "GLM-5.2"
    assert data["status"] == "可用"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_model_duplicate(client):
    payload = {"name": "DupModel", "model_type": "开源", "api_endpoint": "http://x.com", "model_identifier": "dup"}
    await client.post("/api/models", json=payload, headers=AUTH_HEADER)
    resp = await client.post("/api/models", json=payload, headers=AUTH_HEADER)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_models(client):
    await client.post("/api/models", json={
        "name": "ListModel", "model_type": "闭源", "api_endpoint": "http://x.com", "model_identifier": "lm"
    }, headers=AUTH_HEADER)
    resp = await client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert len(data["models"]) >= 1


@pytest.mark.asyncio
async def test_register_model_no_auth(client):
    resp = await client.post("/api/models", json={
        "name": "NoAuth", "model_type": "开源", "api_endpoint": "http://x.com", "model_identifier": "na"
    })
    assert resp.status_code in (401, 403)
