from datetime import datetime, timezone
from app.repositories.memory import missions, generate_id
from app.schemas.mission import MissionStatus

def create_mission(data):
    mission_id = generate_id("missions")

    mission = {
        "id": mission_id,
        "station": data.station,
        "people_count": data.people_count,
        "status": MissionStatus.CREATED,
        "created_at": datetime.now(timezone.utc)
    }

    missions[mission_id] = mission

    return mission

def list_missions():
    return list(missions.values())

def get_mission(mission_id):
    return missions.get(mission_id)