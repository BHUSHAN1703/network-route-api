from datetime import datetime

from pydantic import BaseModel


class ShortestRouteRequest(BaseModel):
    source: str
    destination: str


class ShortestRouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class RouteHistoryResponse(BaseModel):
    id: int
    source: str
    destination: str
    total_latency: float
    path: list[str]
    created_at: datetime