from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class MissionEventResponse(BaseModel):
    id: int
    mission_id: int
    request_id: Optional[int]
    event_type: str
    description: str
    timestamp: datetime
    details: Dict[str, Any]