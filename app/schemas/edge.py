from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EdgeCreate(BaseModel):
    source: str
    destination: str
    latency: float


class EdgeResponse(BaseModel):
    id: int
    source: str
    destination: str
    latency: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)