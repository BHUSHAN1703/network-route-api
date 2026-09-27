from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class RouteHistory(Base):
    __tablename__ = "route_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    total_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    path: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )