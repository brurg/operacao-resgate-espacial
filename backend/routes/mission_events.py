from typing import List
from fastapi import APIRouter, HTTPException
from backend.schemas.mission_event import MissionEventResponse
from backend.services import mission_event
from backend.repositories.memory import missions

router = APIRouter(
    prefix="/missions",
    tags=["Mission Events"]
)

@router.get("/{mission_id}/events", response_model=List[MissionEventResponse])
def list_mission_events(mission_id: int):
    if mission_id not in missions:
        raise HTTPException(
            status_code=404,
            detail="Missão não encontrada"
        )

    return mission_event.list_mission_events(mission_id)