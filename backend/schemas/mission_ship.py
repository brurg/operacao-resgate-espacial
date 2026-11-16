from pydantic import BaseModel, Field
from datetime import datetime

class MissionShipCreate(BaseModel):
    mission_id: int
    ship_id: int
    offered_seats: int = Field(gt=0)
    arrival_time: datetime

class MissionShipResponse(BaseModel):
    id: int
    mission_id: int
    ship_id: int
    ship_name: str
    offered_seats: int
    arrival_time: datetime
    status: str
