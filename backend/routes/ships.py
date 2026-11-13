from fastapi import APIRouter, HTTPException, status
from app.schemas.ship import ShipCreate, ShipResponse
from app.services import ship

router = APIRouter(
    prefix="/ships",
    tags=["Ships"]
)

@router.post("/", response_model=ShipResponse, status_code=status.HTTP_201_CREATED
)
def create_ship(data: ShipCreate):
    return ship.create_ship(data)

@router.get("/", response_model=list[ShipResponse])
def list_ships():
    return ship.list_ships()

@router.get("/{ship_id}", response_model=ShipResponse)
def get_ship(ship_id: int):
    ship_data = ship.get_ship(ship_id)

    if ship_data is None:
        raise HTTPException(
            status_code=404,
            detail="Ship not found"
        )

    return ship_data