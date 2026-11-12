from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.mission_ship import MissionShipCreate, MissionShipResponse
from app.services import mission_ship

router = APIRouter(
    prefix="/mission-ships",
    tags=["Mission Ships"]
)

@router.post("/", response_model=MissionShipResponse, status_code=201)
def offer_ship(data: MissionShipCreate):
    try:
        return mission_ship.offer_ship(
            mission_id=data.mission_id,
            ship_id=data.ship_id,
            offered_seats=data.offered_seats,
            arrival_time=data.arrival_time
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/", response_model=List[MissionShipResponse])
def list_offers(mission_id: int):
    return mission_ship.list_mission_ships(mission_id)

@router.get("/{offer_id}", response_model=MissionShipResponse)
def get_offer(offer_id: int):
    offer = mission_ship.get_mission_ship(offer_id)

    if offer is None:
        raise HTTPException(
            status_code=404,
            detail="Oferta não encontrada"
        )

    return offer