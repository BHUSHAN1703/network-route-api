# Network Route Optimization API

A REST API for managing network nodes and directed edges and finding the lowest-latency route between two nodes.

The project is built with FastAPI and PostgreSQL, with SQLAlchemy used for database access and Alembic for migrations. Shortest routes are calculated using Dijkstra's algorithm since all edge latencies are required to be positive.

## Features

* Create and manage network nodes
* Create and manage directed network edges
* Validate duplicate nodes and edges
* Validate that source and destination nodes exist
* Validate positive edge latency
* Calculate shortest routes using Dijkstra's algorithm
* Store every successful route calculation in route history
* Filter route history by source, destination, date range, and limit
* Dockerized API and PostgreSQL database
* Automated API tests using pytest
* Interactive API documentation through Swagger UI

## Tech Stack

* **Python 3.12**
* **FastAPI**
* **SQLAlchemy 2.x**
* **PostgreSQL 16**
* **Alembic**
* **Pydantic**
* **pytest**
* **Docker / Docker Compose**

## Project Structure

```text
network-route-api/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       ├── nodes.py
│   │       ├── edges.py
│   │       └── routes.py
│   ├── db/
│   │   ├── database.py
│   │   └── models/
│   │       ├── node.py
│   │       ├── edge.py
│   │       └── route_history.py
│   ├── schemas/
│   │   ├── node.py
│   │   ├── edge.py
│   │   └── route.py
│   └── services/
│       └── shortest_path.py
├── tests/
│   ├── conftest.py
│   ├── test_nodes.py
│   ├── test_edges.py
│   └── test_routes.py
├── alembic/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Architecture

The application follows a simple layered structure:

```text
Client
  |
  v
FastAPI Routes
  |
  v
Service Layer
  |
  v
SQLAlchemy
  |
  v
PostgreSQL
```

The shortest-path calculation is kept in a separate service so that the route handling code is not responsible for the graph algorithm itself.

## Database Design

The application uses three main tables.

### Nodes

Stores the network nodes.

```text
nodes
----------------
id
name
created_at
```

Node names are unique.

### Edges

Stores directed connections between nodes.

```text
edges
----------------
id
source_id
destination_id
latency
created_at
```

An edge represents a directed connection:

```text
ServerA -> ServerB
```

The reverse connection is not automatically created.

A unique constraint prevents duplicate edges between the same source and destination.

### Route History

Stores successful shortest-route calculations.

```text
route_history
----------------
id
source
target
total_cost
path
created_at
```

The API exposes these fields as `source`, `destination`, `total_latency`, and `path`.

## API Endpoints

### Create Node

```http
POST /nodes
```

Request:

```json
{
  "name": "ServerA"
}
```

Response:

```json
{
  "id": 1,
  "name": "ServerA",
  "created_at": "2026-09-27T15:00:00"
}
```

---

### Get Nodes

```http
GET /nodes
```

Returns all registered nodes.

---

### Delete Node

```http
DELETE /nodes/{id}
```

Deletes a node and its connected edges.

---

### Create Edge

```http
POST /edges
```

Request:

```json
{
  "source": "ServerA",
  "destination": "ServerB",
  "latency": 12.5
}
```

Response:

```json
{
  "id": 1,
  "source": "ServerA",
  "destination": "ServerB",
  "latency": 12.5,
  "created_at": "2026-09-27T15:10:00"
}
```

---

### Get Edges

```http
GET /edges
```

Returns all configured network edges.

---

### Delete Edge

```http
DELETE /edges/{id}
```

Deletes the specified edge.

---

### Find Shortest Route

```http
POST /routes/shortest
```

Request:

```json
{
  "source": "ServerA",
  "destination": "ServerD"
}
```

Example response:

```json
{
  "total_latency": 23.4,
  "path": [
    "ServerA",
    "ServerB",
    "ServerD"
  ]
}
```

If no route exists, the API returns a `404` response.

---

### Route History

```http
GET /routes/history
```

Optional query parameters:

```text
source
destination
limit
date_from
date_to
```

Example:

```http
GET /routes/history?source=ServerA&destination=ServerD&limit=10
```

Example response:

```json
[
  {
    "id": 1,
    "source": "ServerA",
    "destination": "ServerD",
    "total_latency": 23.4,
    "path": [
      "ServerA",
      "ServerB",
      "ServerD"
    ],
    "created_at": "2026-09-27T15:20:00"
  }
]
```

## Shortest Path Algorithm

Dijkstra's algorithm is used to calculate the shortest route.

The graph is represented using an adjacency list:

```text
ServerA
  |
  +-- ServerB (10)
  |
  +-- ServerD (50)
```

For each node, the algorithm keeps track of the lowest known latency from the source. A priority queue is used to process the node with the smallest current distance first.

Because the API only accepts
