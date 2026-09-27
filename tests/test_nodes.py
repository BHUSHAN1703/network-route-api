from fastapi.testclient import TestClient


def test_create_node(client: TestClient):
    response = client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "ServerA"
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_node(client: TestClient):
    client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    response = client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_multiple_nodes(client: TestClient):
    response1 = client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    response2 = client.post(
        "/nodes",
        json={"name": "ServerB"},
    )

    assert response1.status_code == 201
    assert response2.status_code == 201


def test_get_nodes(client: TestClient):
    client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    client.post(
        "/nodes",
        json={"name": "ServerB"},
    )

    response = client.get("/nodes")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "ServerA"
    assert data[1]["name"] == "ServerB"


def test_delete_node(client: TestClient):
    create_response = client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    node_id = create_response.json()["id"]

    response = client.delete(
        f"/nodes/{node_id}"
    )

    assert response.status_code == 204

    get_response = client.get("/nodes")

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_delete_nonexistent_node(client: TestClient):
    response = client.delete("/nodes/9999")

    assert response.status_code == 404