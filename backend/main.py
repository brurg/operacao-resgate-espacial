from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import (
    missions,
    ships,
    mission_ships,
    rescue_requests,
    mission_events
)

app = FastAPI(
    title="Operação Resgate Espacial",
    description="API para gerenciamento de missões de evacuação espacial.",
    version="1.0.0"
)

app.include_router(missions.router)
app.include_router(ships.router)
app.include_router(mission_ships.router)
app.include_router(rescue_requests.router)
app.include_router(mission_events.router)

@app.get("/", tags=["Health"])
def root():

    return {
        "message": "Operação Resgate Espacial API is up"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)