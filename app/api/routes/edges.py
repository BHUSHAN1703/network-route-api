from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.edge import Edge
from app.db.models.node import Node
from app.schemas.edge import EdgeCreate, EdgeResponse


router = APIRouter(
    prefix="/edges",
    tags=["Edges"],
)


@router.post(
    "",
    response_model=EdgeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_edge(
    edge_data: EdgeCreate,
    db: Session = Depends(get_db),
):
    if edge_data.latency <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latency must be greater than 0",
        )

    source_node = db.scalar(
        select(Node).where(Node.name == edge_data.source)
    )

    if not source_node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source node '{edge_data.source}' not found",
        )

    destination_node = db.scalar(
        select(Node).where(Node.name == edge_data.destination)
    )

    if not destination_node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Destination node '{edge_data.destination}' not found",
        )

    existing_edge = db.scalar(
        select(Edge).where(
            Edge.source_id == source_node.id,
            Edge.destination_id == destination_node.id,
        )
    )

    if existing_edge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Edge from '{edge_data.source}' "
                f"to '{edge_data.destination}' already exists"
            ),
        )

    edge = Edge(
        source_id=source_node.id,
        destination_id=destination_node.id,
        latency=edge_data.latency,
    )

    db.add(edge)
    db.commit()
    db.refresh(edge)

    return EdgeResponse(
        id=edge.id,
        source=edge_data.source,
        destination=edge_data.destination,
        latency=edge.latency,
        created_at=edge.created_at,
    )




@router.get(
    "",
    response_model=list[EdgeResponse],
)
def get_edges(
    db: Session = Depends(get_db),
):
    edges = db.scalars(
        select(Edge).order_by(Edge.id)
    ).all()

    response = []

    for edge in edges:
        source_node = db.get(Node, edge.source_id)
        destination_node = db.get(Node, edge.destination_id)

        response.append(
            EdgeResponse(
                id=edge.id,
                source=source_node.name,
                destination=destination_node.name,
                latency=edge.latency,
                created_at=edge.created_at,
            )
        )

    return response


@router.delete(
    "/{edge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_edge(
    edge_id: int,
    db: Session = Depends(get_db),
):
    edge = db.get(Edge, edge_id)

    if not edge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Edge with id {edge_id} not found",
        )

    db.delete(edge)
    db.commit()

    return None