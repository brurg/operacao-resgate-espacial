import pytest
from backend.repositories import memory
from backend.schemas.mission import MissionStatus
from backend.services import rescue_request

def test_create_valid_mission(client, now):
    response = client.post("/missions/", json={
        "name": "Resgate Aurora", "station": "Aurora", "people_count": 12,
        "urgency": "HIGH",
    })
    assert response.status_code == 201
    assert response.json() == {
        "id": 1, "name": "Resgate Aurora", "station": "Aurora",
        "people_count": 12, "urgency": "HIGH", "status": "CREATED",
        "created_at": now.isoformat().replace("+00:00", "Z"),
    }

def test_default_urgency_is_medium(client):
    response = client.post("/missions/", json={
        "name": "Resgate", "station": "Aurora", "people_count": 1,
    })
    assert response.status_code == 201
    assert response.json()["urgency"] == "MEDIUM"

@pytest.mark.parametrize("people", [0, -1, -100, 1.5, "inválido", None])
def test_invalid_people_rejected_without_mutation(client, snapshot, people):
    before = snapshot()
    response = client.post("/missions/", json={
        "name": "Resgate", "station": "Aurora", "people_count": people,
    })
    assert response.status_code == 422
    assert snapshot() == before

def test_invalid_urgency_rejected(client, snapshot):
    before = snapshot()
    response = client.post("/missions/", json={
        "name": "Resgate", "station": "Aurora", "people_count": 1, "urgency": "URGENT",
    })
    assert response.status_code == 422
    assert snapshot() == before

def test_list_and_get_missions(client, make_mission):
    assert client.get("/missions/").json() == []
    targets = [make_mission(name="Primeira"), make_mission(name="Segunda")]
    listing = client.get("/missions/")
    assert listing.status_code == 200
    assert {item["id"] for item in listing.json()} == {m["id"] for m in targets}
    for target in targets:
        result = client.get(f"/missions/{target['id']}")
        assert result.status_code == 200
        assert result.json()["name"] == target["name"]
    assert client.get("/missions/999").status_code == 404

def test_mission_only_completes_after_all_confirmations(make_mission, make_ship, make_offer):
    target = make_mission(people=10)
    assert target["status"] == MissionStatus.CREATED
    offers = [make_offer(target, make_ship(capacity=5)) for _ in range(2)]
    requests = [rescue_request.create_request(target["id"], offer["id"], 5)
                for offer in offers]
    assert target["status"] == MissionStatus.IN_PROGRESS
    assert rescue_request.get_mission_seat_summary(target["id"])["uncommitted_seats"] == 0
    rescue_request.register_response(requests[0]["id"], 5)
    assert target["status"] == MissionStatus.IN_PROGRESS
    rescue_request.register_response(requests[1]["id"], 5)
    assert target["status"] == MissionStatus.COMPLETED
    completed = [e for e in memory.events.values() if e["event_type"] == "MISSION_COMPLETED"]
    assert len(completed) == 1

@pytest.mark.parametrize("outcome", ["partial", "refuse", "cancel", "expire"])
def test_insufficient_seats_do_not_complete_mission(pending_request, now, outcome):
    target, _, _, request = pending_request(people=5, seats=5, expires_at=now)
    if outcome == "partial":
        rescue_request.register_response(request["id"], 2)
    elif outcome == "refuse":
        rescue_request.register_response(request["id"], 0)
    elif outcome == "cancel":
        rescue_request.cancel_request(request["id"])
    else:
        rescue_request.expire_request(request["id"])
    assert target["status"] == MissionStatus.IN_PROGRESS

def test_mission_events_are_filtered_and_chronological(client, clock, make_mission, make_ship, make_offer):
    target = make_mission(people=4)
    other = make_mission()
    offer = make_offer(target, make_ship(capacity=4), automatic=True)
    request = next(iter(memory.requests.values()))
    clock.current = clock.current.replace(hour=13)
    rescue_request.register_response(request["id"], 4)
    response = client.get(f"/missions/{target['id']}/events")
    assert response.status_code == 200
    events = response.json()
    assert [e["event_type"] for e in events] == [
        "SHIP_OFFERED", "REQUEST_CREATED", "REQUEST_RESPONDED", "MISSION_COMPLETED",
    ]
    assert all(e["mission_id"] == target["id"] for e in events)
    assert [e["timestamp"] for e in events] == sorted(e["timestamp"] for e in events)
    assert events[0]["details"]["ship_id"] == offer["ship_id"]
    assert client.get(f"/missions/{other['id']}/events").json() == []
    assert client.get("/missions/999/events").status_code == 404