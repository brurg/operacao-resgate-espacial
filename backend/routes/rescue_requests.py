from typing import List
from fastapi import APIRouter, HTTPException
from backend.schemas.rescue_request import (
    RescueRequestCreate,
    RescueResponseCreate,
    RescueRequestResponse,
    MissionSummaryResponse
)
from backend.services import rescue_request

router = APIRouter(
    prefix="/requests",
    tags=["Rescue Requests"]
)

@router.post("/", response_model=RescueRequestResponse, status_code=201)
def create_request(data: RescueRequestCreate):
    try:
        request = rescue_request.create_request(
            mission_id=data.mission_id,
            mission_ship_id=data.mission_ship_id,
            requested_seats=data.requested_seats,
            expires_at=data.expires_at
        )
        return rescue_request.add_mission_urgency(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/", response_model=List[RescueRequestResponse])
def list_requests(mission_id: int = None):
    return rescue_request.list_requests(mission_id)

@router.get("/{request_id}", response_model=RescueRequestResponse)
def get_request(request_id: int):
    request = rescue_request.get_request(request_id)

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Solicitação não encontrada"
        )

    return request

@router.post("/{request_id}/response", response_model=RescueRequestResponse)
def register_response(
    request_id: int,
    data: RescueResponseCreate
):
    try:
        request = rescue_request.register_response(
            request_id,
            data.confirmed_seats
        )
        return rescue_request.add_mission_urgency(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/{request_id}/cancel", response_model=RescueRequestResponse)
def cancel_request(request_id: int):
    try:
        request = rescue_request.cancel_request(request_id)
        return rescue_request.add_mission_urgency(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/{request_id}/expire", response_model=RescueRequestResponse)
def expire_request(request_id: int):
    try:
        request = rescue_request.expire_request(request_id)
        return rescue_request.add_mission_urgency(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get(
    "/mission/{mission_id}/summary",
    response_model=MissionSummaryResponse
)
def get_mission_summary(mission_id: int):
    try:
        return rescue_request.get_mission_seat_summary(mission_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))