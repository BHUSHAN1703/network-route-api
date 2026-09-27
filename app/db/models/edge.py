from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Edge(Base):
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(primary_key=True)

    source_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id"),
        nullable=False,
    )

    destination_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id"),
        nullable=False,
    )

    latency: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "destination_id",
            name="uq_edge_source_destination",
        ),
    )