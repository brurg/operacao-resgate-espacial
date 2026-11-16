import pytest
from backend.repositories import memory
from backend.services import mission_ship, rescue_request

def test_offer_triggers_distribution_and_can_be_queried(client, make_mission, make_ship, now):
    target = make_mission(people=8)
    vessel = make_ship(capacity=10)
    response = client.post("/mission-ships/", json={
        "mission_id": target["id"], "ship_id": vessel["id"],
        "offered_seats": 6, "arrival_time": now.isoformat(),
    })
    assert response.status_code == 201
    offer = response.json()
    assert offer["status"] == "REQUESTED"
    assert offer["offered_seats"] == 6
    assert offer["ship_name"] == vessel["name"]
    assert client.get(f"/mission-ships/{offer['id']}").json() == offer
    assert client.get("/mission-ships/", params={"mission_id": target["id"]}).json() == [offer]
    assert client.get("/mission-ships/", params={"mission_id": 999}).json() == []
    assert client.get("/mission-ships/999").status_code == 404
    assert len(memory.requests) == 1
    assert next(iter(memory.requests.values()))["requested_seats"] == 6

@pytest.mark.parametrize("seats", [0, -1, 1.5, "inválido", None])
def test_invalid_offer_schema(client, make_mission, make_ship, now, snapshot, seats):
    target, vessel = make_mission(), make_ship()
    before = snapshot()
    response = client.post("/mission-ships/", json={
        "mission_id": target["id"], "ship_id": vessel["id"],
        "offered_seats": seats, "arrival_time": now.isoformat(),
    })
    assert response.status_code == 422
    assert snapshot() == before

@pytest.mark.parametrize("seats", [0, -1, 1.5, True, "2", None, 11])
def test_offer_service_rejects_invalid_quantity(make_mission, make_ship, now, snapshot, seats):
    target, vessel = make_mission(), make_ship(capacity=10)
    before = snapshot()
    with pytest.raises(ValueError):
        mission_ship.offer_ship(target["id"], vessel["id"], seats, now)
    assert snapshot() == before

@pytest.mark.parametrize("missing", ["mission", "ship"])
def test_offer_requires_existing_entities(client, make_mission, make_ship, now, snapshot, missing):
    target, vessel = make_mission(), make_ship()
    before = snapshot()
    response = client.post("/mission-ships/", json={
        "mission_id": 999 if missing == "mission" else target["id"],
        "ship_id": 999 if missing == "ship" else vessel["id"],
        "offered_seats": 1, "arrival_time": now.isoformat(),
    })
    assert response.status_code == 400
    assert response.json()["detail"] == ("Missão não encontrada" if missing == "mission" else "Nave não encontrada")
    assert snapshot() == before

def test_offer_cannot_exceed_total_capacity(client, make_mission, make_ship, now, snapshot):
    target, vessel = make_mission(), make_ship(capacity=5)
    before = snapshot()
    response = client.post("/mission-ships/", json={
        "mission_id": target["id"], "ship_id": vessel["id"],
        "offered_seats": 6, "arrival_time": now.isoformat(),
    })
    assert response.status_code == 400
    assert "supera a capacidade total" in response.json()["detail"]
    assert snapshot() == before

def test_duplicate_ship_offer_in_same_mission_rejected(make_mission, make_ship, make_offer, now, snapshot):
    target, vessel = make_mission(), make_ship()
    make_offer(target, vessel, seats=3, automatic=True)
    before = snapshot()
    with pytest.raises(ValueError, match="já disponibilizada"):
        mission_ship.offer_ship(target["id"], vessel["id"], 3, now)
    assert snapshot() == before

def test_completed_mission_rejects_offer(pending_request, make_ship, now, snapshot):
    target, _, _, request = pending_request(people=5, seats=5)
    rescue_request.register_response(request["id"], 5)
    vessel = make_ship()
    before = snapshot()
    with pytest.raises(ValueError, match="missão concluída"):
        mission_ship.offer_ship(target["id"], vessel["id"], 1, now)
    assert snapshot() == before

def test_same_ship_serves_different_missions_with_shared_capacity(make_mission, make_ship, make_offer):
    first, second = make_mission(people=6), make_mission(people=6)
    vessel = make_ship(capacity=10)
    offers = [make_offer(target, vessel, seats=6, automatic=True)
              for target in (first, second)]
    requests = list(memory.requests.values())
    assert [r["requested_seats"] for r in requests] == [6, 4]
    assert [r["mission_ship_id"] for r in requests] == [o["id"] for o in offers]
    assert rescue_request.get_ship_committed_seats(vessel["id"]) == 10
    assert rescue_request.get_ship_available_capacity(vessel["id"]) == 0