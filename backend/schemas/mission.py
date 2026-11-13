from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class MissionStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class MissionCreate(BaseModel):
    station: str
    people_count: int = Field(gt=0)

class MissionResponse(BaseModel):
    id: int
    station: str
    people_count: int
    status: MissionStatus
    created_at: datetime