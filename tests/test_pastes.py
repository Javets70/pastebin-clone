import pytest


@pytest.mark.asyncio
async def test_create_paste(client):
    """Test creating a new paste"""
    response = await client.post(
        "/api/v1/pastes/",
        json={"title": "Test Paste", "content": "Hello World!", "language": "python"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Paste"
    assert data["content"] == "Hello World!"
    assert "short_code" in data


@pytest.mark.asyncio
async def test_get_paste(client):
    """Test retrieving a paste"""
    # Create paste first
    create_response = await client.post("/api/v1/pastes/", json={"content": "Test content"})
    short_code = create_response.json()["short_code"]

    # Get paste
    response = await client.get(f"/api/v1/pastes/{short_code}")
    assert response.status_code == 200
    assert response.json()["content"] == "Test content"


@pytest.mark.asyncio
async def test_get_nonexistent_paste(client):
    """Test getting a paste that doesn't exist"""
    response = await client.get("/api/v1/pastes/notfound")
    assert response.status_code == 404
