from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.node import Node
from app.db.models.edge import Edge
from app.schemas.node import NodeCreate, NodeResponse


router = APIRouter(
    prefix="/nodes",
    tags=["Nodes"],
)


@router.post(
    "",
    response_model=NodeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_node(
    node_data: NodeCreate,
    db: Session = Depends(get_db),
):
    existing_node = db.scalar(
        select(Node).where(Node.name == node_data.name)
    )

    if existing_node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node '{node_data.name}' already exists",
        )

    node = Node(name=node_data.name)

    db.add(node)
    db.commit()
    db.refresh(node)

    return node

@router.get(
    "",
    response_model=list[NodeResponse],
)
def get_nodes(
    db: Session = Depends(get_db),
):
    nodes = db.scalars(
        select(Node).order_by(Node.id)
    ).all()

    return nodes


@router.delete(
    "/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_node(
    node_id: int,
    db: Session = Depends(get_db),
):
    node = db.get(Node, node_id)

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with id {node_id} not found",
        )

    connected_edges = db.scalars(
        select(Edge).where(
            (Edge.source_id == node_id)
            | (Edge.destination_id == node_id)
        )
    ).all()

    for edge in connected_edges:
        db.delete(edge)

    db.delete(node)
    db.commit()

    return None