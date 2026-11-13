from fastapi import APIRouter, HTTPException, status
from backend.schemas.mission import MissionCreate, MissionResponse
from backend.services import mission

router = APIRouter(
    prefix="/missions",
    tags=["Missions"]
)

@router.post("/", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
def create_mission(data: MissionCreate):
    return mission.create_mission(data)

@router.get("/", response_model=list[MissionResponse])
def list_missions():
    return mission.list_missions()


@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int):
    mission = mission.get_mission(mission_id)

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    return mission