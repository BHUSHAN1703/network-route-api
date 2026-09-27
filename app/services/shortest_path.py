import heapq
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.edge import Edge
from app.db.models.node import Node


def find_shortest_path(
    db: Session,
    source: Node,
    destination: Node,
) -> tuple[float, list[str]] | None:

    # Build graph from database edges
    edges = db.scalars(select(Edge)).all()

    graph = defaultdict(list)

    for edge in edges:
        graph[edge.source_id].append(
            (edge.destination_id, edge.latency)
        )

    # source == destination
    if source.id == destination.id:
        return 0.0, [source.name]

    # Priority queue: (total_latency, node_id, path)
    queue = [(0.0, source.id, [source.id])]

    # Best known distance to each node
    distances = {
        source.id: 0.0
    }

    while queue:
        current_distance, current_node_id, path = heapq.heappop(queue)

        # Skip outdated queue entries
        if current_distance > distances.get(
            current_node_id,
            float("inf"),
        ):
            continue

        # Destination reached
        if current_node_id == destination.id:
            node_names = db.scalars(
                select(Node).where(Node.id.in_(path))
            ).all()

            node_name_map = {
                node.id: node.name
                for node in node_names
            }

            return (
                current_distance,
                [node_name_map[node_id] for node_id in path],
            )

        # Explore neighbors
        for neighbor_id, latency in graph[current_node_id]:

            new_distance = current_distance + latency

            if new_distance < distances.get(
                neighbor_id,
                float("inf"),
            ):
                distances[neighbor_id] = new_distance

                heapq.heappush(
                    queue,
                    (
                        new_distance,
                        neighbor_id,
                        path + [neighbor_id],
                    ),
                )

    # No path exists
    return None