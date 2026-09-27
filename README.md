# Network Route Optimization API

A backend API for managing network nodes and connections and finding the shortest route based on network latency.

## Tech Stack

* Python 3.12
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* Docker / Docker Compose
* Pytest

## Features

* Create network nodes
* Create directed network edges
* Calculate shortest route using Dijkstra's algorithm
* Store successful route queries in history
* Filter route history
* List nodes and edges
* Delete nodes and edges
* Input validation and error handling
* API documentation through Swagger

## API Endpoints

### Required

```text
POST /nodes
POST /edges
POST /routes/shortest
GET  /routes/history
```

### Optional

```text
GET    /nodes
GET    /edges
DELETE /nodes/{id}
DELETE /edges/{id}
```

## Shortest Path

Dijkstra's algorithm is used for route calculation.

Since latency values are always positive, Dijkstra is suitable for this use case.

The graph is treated as directed:

```text
ServerA → ServerB
```

does not automatically create:

```text
ServerB → ServerA
```

The implementation uses a min-heap to process the node with the lowest current latency.

## Database

Three main tables are used:

* `nodes`
* `edges`
* `route_history`

Edges store references to source and destination nodes.

Duplicate directed edges are not allowed.

Route history stores the calculated path, total latency and timestamp.

## Assumptions

* Node names are unique.
* Source and destination nodes must exist before creating an edge.
* Latency must be greater than zero.
* Edges are directional.
* Reverse edges are allowed separately.
* Duplicate edges in the same direction are rejected.
* Successful route calculations are stored in history.
* Failed route searches are not stored.
* Deleting a node also removes its connected edges.
* Historical route records are retained after node deletion.
* A route from a node to itself has zero latency.
* Authentication was not required, so it was not implemented.
* Pagination was not required for nodes or edges.
* PostgreSQL is used for the application.
* Tests use an isolated test database.

## Design Decision

I did not create a repository layer for this assignment because the database operations are small and straightforward.

**For more complex business logic or larger applications, I would introduce a repository layer to separate database access from the API/service layer.**

The shortest-path calculation is kept separately in the service layer because it contains the main algorithmic logic.

## Running Locally

Start the application using Docker:

```bash
docker compose up -d --build
```

Run migrations:

```bash
docker compose exec api alembic upgrade head
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## Tests

Run:

```bash
docker compose exec api pytest -v
```

Current test suite:

```text
25 tests passed
```

Tests cover node, edge, shortest-route, history and optional API behaviour.

The pytest cases were created with AI assistance and then tested against the application.

AI assistance was also used while troubleshooting some local Docker/Python setup and import issues.

## Migrations

Create a migration:

```bash
docker compose exec api alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
docker compose exec api alembic upgrade head
```

Rollback:

```bash
docker compose exec api alembic downgrade -1
```

## Error Handling

Examples include:

* Duplicate node → `400`
* Invalid latency → `400`
* Missing node → `400`
* Duplicate edge → `400`
* No route available → `404`

Example no-route response:

```json
{
  "error": "No path exists between ServerA and ServerD"
}
```

## Future Improvements

For a larger production system I would consider:

* Repository/data-access layer
* Authentication and authorization
* Pagination
* Better graph loading for very large networks
* Caching frequently requested routes
* Structured logging and monitoring
* CI/CD
* Performance and load testing

The implementation intentionally stays within the scope of the assignment rather than adding unnecessary infrastructure.
