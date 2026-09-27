from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NodeCreate(BaseModel):
    name: str


class NodeResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)