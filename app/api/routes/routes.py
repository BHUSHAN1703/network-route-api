from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session
import json
from app.db.database import get_db
from app.db.models.node import Node
from app.schemas.route import (
    RouteHistoryResponse,
    ShortestRouteRequest,
    ShortestRouteResponse,
)
from app.services.shortest_path import find_shortest_path
from app.db.models.route_history import RouteHistory

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post(
    "/shortest",
    response_model=ShortestRouteResponse,
    status_code=status.HTTP_200_OK,
)
def get_shortest_route(
    route_data: ShortestRouteRequest,
    db: Session = Depends(get_db),
):
    # Find source node
    source_node = db.scalar(
        select(Node).where(Node.name == route_data.source)
    )

    if not source_node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source node '{route_data.source}' not found",
        )

    # Find destination node
    destination_node = db.scalar(
        select(Node).where(Node.name == route_data.destination)
    )

    if not destination_node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Destination node '{route_data.destination}' not found",
        )

    # Find shortest path
    result = find_shortest_path(
        db,
        source_node,
        destination_node,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No path exists between "
                f"{route_data.source} and {route_data.destination}"
            ),
        )

    total_latency, path = result
    history = RouteHistory(
    source=source_node.name,
    target=destination_node.name,
    total_cost=total_latency,
    path=path,
)
    db.add(history)
    db.commit()
    return ShortestRouteResponse(
        total_latency=total_latency,
        path=path,
    )


@router.get(
    "/history",
    response_model=list[RouteHistoryResponse],
)
def get_route_history(
    source: str | None = Query(default=None),
    destination: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(RouteHistory)

    if source:
        query = query.where(RouteHistory.source == source)

    if destination:
        query = query.where(RouteHistory.target == destination)

    if date_from:
        query = query.where(
            RouteHistory.created_at >= date_from
        )

    if date_to:
        query = query.where(
            RouteHistory.created_at <= date_to
        )

    query = (
        query
        .order_by(RouteHistory.created_at.desc())
        .limit(limit)
    )

    history_records = db.scalars(query).all()

    history_response = []

    for record in history_records:
        path = record.path

        if isinstance(path, str):
            path = json.loads(path)

        history_response.append(
            RouteHistoryResponse(
                id=record.id,
                source=record.source,
                destination=record.target,
                total_latency=record.total_cost,
                path=path,
                created_at=record.created_at,
            )
        )

    return history_response