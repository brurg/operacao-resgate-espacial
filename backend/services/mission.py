from datetime import datetime, timezone
from backend.repositories.memory import missions, generate_id, lock
from backend.schemas.mission import MissionStatus

def create_mission(data):
    with lock:
        mission_id = generate_id("missions")

        mission = {
            "id": mission_id,
            "name": data.name,
            "station": data.station,
            "people_count": data.people_count,
            "urgency": data.urgency,
            "status": MissionStatus.CREATED,
            "created_at": datetime.now(timezone.utc)
        }

        missions[mission_id] = mission

        from backend.services.strategy import execute_strategy
        execute_strategy()

        return mission

def list_missions():
    with lock:
        return list(missions.values())

def get_mission(mission_id):
    with lock:
        return missions.get(mission_id)