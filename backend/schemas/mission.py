from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class MissionStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class MissionUrgency(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class MissionCreate(BaseModel):
    name: str
    station: str
    people_count: int = Field(gt=0)
    urgency: MissionUrgency = MissionUrgency.MEDIUM

class MissionResponse(BaseModel):
    id: int
    name: str
    station: str
    people_count: int
    urgency: MissionUrgency
    status: MissionStatus
    created_at: datetime