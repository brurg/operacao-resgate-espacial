from pydantic import BaseModel, Field

class ShipCreate(BaseModel):
    name: str
    total_capacity: int = Field(gt=0)

class ShipResponse(BaseModel):
    id: int
    name: str
    total_capacity: int