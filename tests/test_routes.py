from fastapi.testclient import TestClient


def create_test_graph(client: TestClient):
    nodes = [
        "ServerA",
        "ServerB",
        "ServerC",
        "ServerD",
    ]

    for name in nodes:
        response = client.post(
            "/nodes",
            json={"name": name},
        )

        assert response.status_code == 201

    edges = [
        {
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 10,
        },
        {
            "source": "ServerB",
            "destination": "ServerC",
            "latency": 15,
        },
        {
            "source": "ServerC",
            "destination": "ServerD",
            "latency": 20,
        },
        {
            "source": "ServerA",
            "destination": "ServerD",
            "latency": 50,
        },
    ]

    for edge in edges:
        response = client.post(
            "/edges",
            json=edge,
        )

        assert response.status_code == 201


def test_shortest_route(client: TestClient):
    create_test_graph(client)

    response = client.post(
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerD",
        },
    )

    assert response.status_code == 200

    data = response.json()

    # A -> B -> C -> D = 10 + 15 + 20 = 45
    assert data["total_latency"] == 45
    assert data["path"] == [
        "ServerA",
        "ServerB",
        "ServerC",
        "ServerD",
    ]


def test_direct_shortest_route(client: TestClient):
    create_test_graph(client)

    response = client.post(
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerD",
        },
    )

    data = response.json()

    assert data["total_latency"] < 50


def test_source_node_not_found(client: TestClient):
    client.post(
        "/nodes",
        json={"name": "ServerB"},
    )

    response = client.post(
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerB",
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
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerB",
        },
    )

    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_no_path_exists(client: TestClient):
    client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    client.post(
        "/nodes",
        json={"name": "ServerB"},
    )

    response = client.post(
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerB",
        },
    )

    assert response.status_code == 404


def test_same_source_and_destination(client: TestClient):
    client.post(
        "/nodes",
        json={"name": "ServerA"},
    )

    response = client.post(
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerA",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_latency"] == 0
    assert data["path"] == ["ServerA"]


def test_route_history(client: TestClient):
    create_test_graph(client)

    response = client.post(
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerD",
        },
    )

    assert response.status_code == 200

    history_response = client.get(
        "/routes/history"
    )

    assert history_response.status_code == 200

    data = history_response.json()

    assert len(data) == 1

    assert data[0]["source"] == "ServerA"
    assert data[0]["destination"] == "ServerD"
    assert data[0]["total_latency"] == 45
    assert data[0]["path"] == [
        "ServerA",
        "ServerB",
        "ServerC",
        "ServerD",
    ]


def test_route_history_source_filter(client: TestClient):
    create_test_graph(client)

    client.post(
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerD",
        },
    )

    response = client.get(
        "/routes/history?source=ServerA"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["source"] == "ServerA"


def test_route_history_destination_filter(client: TestClient):
    create_test_graph(client)

    client.post(
        "/routes/shortest",
        json={
            "source": "ServerA",
            "destination": "ServerD",
        },
    )

    response = client.get(
        "/routes/history?destination=ServerD"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["destination"] == "ServerD"


def test_route_history_limit(client: TestClient):
    create_test_graph(client)

    for _ in range(3):
        response = client.post(
            "/routes/shortest",
            json={
                "source": "ServerA",
                "destination": "ServerD",
            },
        )

        assert response.status_code == 200

    response = client.get(
        "/routes/history?limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2