from fastapi.testclient import TestClient


def create_nodes(client: TestClient):
    client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    client.post(
        "/nodes",
        json={"name": "ServerB"},
    )


def test_create_edge(client: TestClient):
    create_nodes(client)

    response = client.post(
        "/edges",
        json={
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["source"] == "ServerA"
    assert data["destination"] == "ServerB"
    assert data["latency"] == 10
    assert "id" in data


def test_invalid_latency(client: TestClient):
    create_nodes(client)

    response = client.post(
        "/edges",
        json={
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 0,
        },
    )

    assert response.status_code == 400
    assert "greater than 0" in response.json()["detail"]


def test_negative_latency(client: TestClient):
    create_nodes(client)

    response = client.post(
        "/edges",
        json={
            "source": "ServerA",
            "destination": "ServerB",
            "latency": -5,
        },
    )

    assert response.status_code == 400


def test_source_node_not_found(client: TestClient):
    client.post(
        "/nodes",
        json={"name": "ServerB"},
    )

    response = client.post(
        "/edges",
        json={
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 10,
        },
    )

    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_destination_node_not_found(client: TestClient):
    client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    response = client.post(
        "/edges",
        json={
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 10,
        },
    )

    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_duplicate_edge(client: TestClient):
    create_nodes(client)

    edge = {
        "source": "ServerA",
        "destination": "ServerB",
        "latency": 10,
    }

    first_response = client.post(
        "/edges",
        json=edge,
    )

    second_response = client.post(
        "/edges",
        json=edge,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert "already exists" in second_response.json()["detail"]


def test_get_edges(client: TestClient):
    create_nodes(client)

    client.post(
        "/edges",
        json={
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 10,
        },
    )

    response = client.get("/edges")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["source"] == "ServerA"
    assert data[0]["destination"] == "ServerB"
    assert data[0]["latency"] == 10


def test_delete_edge(client: TestClient):
    create_nodes(client)

    create_response = client.post(
        "/edges",
        json={
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 10,
        },
    )

    edge_id = create_response.json()["id"]

    response = client.delete(
        f"/edges/{edge_id}"
    )

    assert response.status_code == 204

    get_response = client.get("/edges")

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_delete_nonexistent_edge(client: TestClient):
    response = client.delete("/edges/9999")

    assert response.status_code == 404