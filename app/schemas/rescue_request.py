from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RescueRequestCreate(BaseModel):
    mission_id: int
    mission_ship_id: int
    requested_seats: int = Field(gt=0)
    expires_at: Optional[datetime] = None

class RescueResponseCreate(BaseModel):
    confirmed_seats: int = Field(ge=0)

class RescueRequestResponse(BaseModel):
    id: int
    mission_id: int
    mission_ship_id: int
    requested_seats: int
    confirmed_seats: int
    status: str
    created_at: datetime
    responded_at: Optional[datetime]
    expires_at: Optional[datetime]

class MissionSummaryResponse(BaseModel):
    people_count: int
    confirmed_seats: int
    pending_seats: int
    missing_seats: int
    uncommitted_seats: int