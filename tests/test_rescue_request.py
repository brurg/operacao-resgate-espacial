from datetime import timedelta
import pytest
from backend.repositories import memory
from backend.services import rescue_request as service

def test_create_request_and_queries(client, make_mission, make_ship, make_offer, now):
    target = make_mission(people=8)
    other = make_mission()
    vessel = make_ship(capacity=10)
    offer = make_offer(target, vessel, seats=6)
    deadline = now + timedelta(minutes=5)
    response = client.post("/requests/", json={
        "mission_id": target["id"], "mission_ship_id": offer["id"],
        "requested_seats": 4, "expires_at": deadline.isoformat(),
    })
    assert response.status_code == 201
    request = response.json()
    assert request["status"] == "PENDING"
    assert request["urgency"] == "MEDIUM"
    assert request["requested_seats"] == 4
    assert request["confirmed_seats"] == 0
    assert request["responded_at"] is None
    assert request["created_at"] == now.isoformat().replace("+00:00", "Z")
    assert request["expires_at"] == deadline.isoformat().replace("+00:00", "Z")
    assert client.get(f"/requests/{request['id']}").json()["urgency"] == "MEDIUM"
    assert client.get("/requests/").json()[0]["urgency"] == "MEDIUM"
    assert client.get("/requests/", params={"mission_id": target["id"]}).json()[0]["urgency"] == "MEDIUM"
    assert client.get("/requests/", params={"mission_id": other["id"]}).json() == []
    assert client.get("/requests/999").status_code == 404
    assert offer["status"] == "REQUESTED"
    assert target["status"] == "IN_PROGRESS"
    assert service.get_ship_available_capacity(vessel["id"]) == 6

@pytest.mark.parametrize("seats", [0, -1, 1.5, "inválido", None])
def test_invalid_request_schema(client, make_mission, make_ship, make_offer, snapshot, seats):
    target = make_mission()
    offer = make_offer(target, make_ship())
    before = snapshot()
    response = client.post("/requests/", json={
        "mission_id": target["id"], "mission_ship_id": offer["id"],
        "requested_seats": seats,
    })
    assert response.status_code == 422
    assert snapshot() == before

@pytest.mark.parametrize("seats", [0, -1, 1.5, True, "2", None])
def test_invalid_request_service_quantity(make_mission, make_ship, make_offer, snapshot, seats):
    target = make_mission()
    offer = make_offer(target, make_ship())
    before = snapshot()
    with pytest.raises(ValueError):
        service.create_request(target["id"], offer["id"], seats)
    assert snapshot() == before

@pytest.mark.parametrize("case,detail", [
    ("mission", "Missão não encontrada"),
    ("offer", "Disponibilidade de nave não encontrada"),
    ("foreign_offer", "A nave não pertence a esta missão"),
    ("above_offer", "A quantidade solicitada supera a oferta da nave"),
    ("above_need", "Não há assentos suficientes ainda não comprometidos"),
])
def test_request_business_errors(client, make_mission, make_ship, make_offer,
                                 snapshot, case, detail):
    target = make_mission(people=5)
    other = make_mission()
    offer = make_offer(target, make_ship(capacity=10), seats=8)
    before = snapshot()
    payload = {"mission_id": target["id"], "mission_ship_id": offer["id"],
               "requested_seats": 2}
    if case == "mission":
        payload["mission_id"] = 999
    elif case == "offer":
        payload["mission_ship_id"] = 999
    elif case == "foreign_offer":
        payload["mission_id"] = other["id"]
    elif case == "above_offer":
        payload["requested_seats"] = 9
    else:
        payload["requested_seats"] = 6
    response = client.post("/requests/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == detail
    assert snapshot() == before

def test_requested_offer_cannot_receive_duplicate_request(pending_request, snapshot):
    target, _, offer, _ = pending_request()
    before = snapshot()
    with pytest.raises(ValueError, match="oferta não está disponível"):
        service.create_request(target["id"], offer["id"], 1)
    assert snapshot() == before

def test_completed_mission_rejects_request(pending_request, make_ship, make_offer, snapshot):
    target, _, _, request = pending_request(people=5, seats=5)
    extra = make_offer(target, make_ship())
    service.register_response(request["id"], 5)
    before = snapshot()
    with pytest.raises(ValueError, match="missão já foi concluída"):
        service.create_request(target["id"], extra["id"], 1)
    assert snapshot() == before

@pytest.mark.parametrize("commitment", ["pending", "confirmed", "partial"])
def test_cannot_request_above_remaining_ship_capacity(make_mission, make_ship, make_offer,
                                                     snapshot, commitment):
    first, second = make_mission(), make_mission()
    vessel = make_ship(capacity=10)
    first_offer = make_offer(first, vessel, seats=8)
    request = service.create_request(first["id"], first_offer["id"], 8)
    if commitment != "pending":
        service.register_response(request["id"], 8 if commitment == "confirmed" else 6)
    second_offer = make_offer(second, vessel, seats=8)
    before = snapshot()
    with pytest.raises(ValueError, match="capacidade disponível suficiente"):
        service.create_request(second["id"], second_offer["id"], 5)
    assert snapshot() == before

@pytest.mark.parametrize("confirmed,status,available", [
    (5, "CONFIRMED", 5), (2, "PARTIAL", 8), (0, "UNAVAILABLE", 10),
])
def test_response_totals_and_capacity(client, pending_request, now, confirmed, status, available):
    target, vessel, offer, request = pending_request(people=10, seats=5, capacity=10)
    response = client.post(f"/requests/{request['id']}/response",
                           json={"confirmed_seats": confirmed})
    assert response.status_code == 200
    assert response.json()["status"] == status
    assert response.json()["urgency"] == "MEDIUM"
    assert response.json()["confirmed_seats"] == confirmed
    assert response.json()["responded_at"] == now.isoformat().replace("+00:00", "Z")
    assert offer["status"] == "UNAVAILABLE"
    assert service.get_ship_available_capacity(vessel["id"]) == available
    assert client.get(f"/requests/mission/{target['id']}/summary").json() == {
        "people_count": 10, "confirmed_seats": confirmed, "pending_seats": 0,
        "missing_seats": 10 - confirmed, "uncommitted_seats": 10 - confirmed,
    }

@pytest.mark.parametrize("confirmed", [-1, 1.5, "inválido", None])
def test_invalid_response_schema(client, pending_request, snapshot, confirmed):
    _, _, _, request = pending_request()
    before = snapshot()
    response = client.post(f"/requests/{request['id']}/response",
                           json={"confirmed_seats": confirmed})
    assert response.status_code == 422
    assert snapshot() == before

@pytest.mark.parametrize("confirmed", [-1, 1.5, True, "2", None, 6])
def test_invalid_response_service_quantity(pending_request, snapshot, confirmed):
    _, _, _, request = pending_request(seats=5)
    before = snapshot()
    with pytest.raises(ValueError):
        service.register_response(request["id"], confirmed)
    assert snapshot() == before

def test_response_above_requested_is_http_400(client, pending_request, snapshot):
    _, _, _, request = pending_request(seats=5)
    before = snapshot()
    response = client.post(f"/requests/{request['id']}/response", json={"confirmed_seats": 6})
    assert response.status_code == 400
    assert "mais assentos que o solicitado" in response.json()["detail"]
    assert snapshot() == before

def test_cancel_pending_request(client, pending_request):
    target, vessel, offer, request = pending_request()
    response = client.post(f"/requests/{request['id']}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
    assert response.json()["urgency"] == "MEDIUM"
    assert offer["status"] == "UNAVAILABLE"
    assert service.get_ship_available_capacity(vessel["id"]) == 10
    assert service.get_mission_seat_summary(target["id"])["pending_seats"] == 0

@pytest.mark.parametrize("naive", [False, True])
@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_expiration_boundary(client, pending_request, now, snapshot, naive, offset):
    deadline = now + timedelta(seconds=offset)
    if naive:
        deadline = deadline.replace(tzinfo=None)
    target, vessel, _, request = pending_request(expires_at=deadline)
    before = snapshot()
    response = client.post(f"/requests/{request['id']}/expire")
    assert response.status_code == (400 if offset > 0 else 200)
    if offset > 0:
        assert "ainda não terminou" in response.json()["detail"]
        assert snapshot() == before
    else:
        assert response.json()["status"] == "EXPIRED"
        assert response.json()["urgency"] == "MEDIUM"
        assert service.get_ship_available_capacity(vessel["id"]) == 10
        assert service.get_mission_seat_summary(target["id"])["pending_seats"] == 0

def test_expiration_requires_deadline(client, pending_request, snapshot):
    _, _, _, request = pending_request()
    before = snapshot()
    response = client.post(f"/requests/{request['id']}/expire")
    assert response.status_code == 400
    assert "não possui prazo" in response.json()["detail"]
    assert snapshot() == before

@pytest.mark.parametrize("final_state", ["CONFIRMED", "PARTIAL", "UNAVAILABLE", "CANCELLED", "EXPIRED"])
@pytest.mark.parametrize("operation", ["response", "cancel", "expire"])
def test_final_states_are_immutable(client, pending_request, now, snapshot, final_state, operation):
    _, _, _, request = pending_request(expires_at=now)
    if final_state == "CANCELLED":
        service.cancel_request(request["id"])
    elif final_state == "EXPIRED":
        service.expire_request(request["id"])
    else:
        service.register_response(request["id"], {"CONFIRMED": 5, "PARTIAL": 2,
                                                 "UNAVAILABLE": 0}[final_state])
    assert request["status"] == final_state
    before = snapshot()
    response = client.post(f"/requests/{request['id']}/{operation}",
                           **({"json": {"confirmed_seats": 5}} if operation == "response" else {}))
    assert response.status_code == 400
    assert snapshot() == before

@pytest.mark.parametrize("operation", ["response", "cancel", "expire"])
def test_missing_request_mutations_are_rejected(client, snapshot, operation):
    before = snapshot()
    response = client.post(f"/requests/999/{operation}",
                           **({"json": {"confirmed_seats": 1}} if operation == "response" else {}))
    assert response.status_code == 400
    assert response.json()["detail"] == "Solicitação não encontrada"
    assert snapshot() == before

def test_summary_separates_guaranteed_pending_and_uncommitted(make_mission, make_ship, make_offer):
    target = make_mission(people=20)
    offers = [make_offer(target, make_ship(capacity=8)) for _ in range(3)]
    first = service.create_request(target["id"], offers[0]["id"], 8)
    second = service.create_request(target["id"], offers[1]["id"], 8)
    service.register_response(first["id"], 3)
    summary = service.get_mission_seat_summary(target["id"])
    assert summary == {"people_count": 20, "confirmed_seats": 3, "pending_seats": 16,
                       "missing_seats": 17, "uncommitted_seats": 1}
    service.register_response(second["id"], 0)
    assert service.get_mission_seat_summary(target["id"]) == {
        "people_count": 20, "confirmed_seats": 3, "pending_seats": 8,
        "missing_seats": 17, "uncommitted_seats": 9,
    }
    assert sum(r["confirmed_seats"] for r in memory.requests.values()) == 3

def test_missing_summary_and_capacity_errors(client):
    assert client.get("/requests/mission/999/summary").status_code == 404
    with pytest.raises(ValueError, match="Nave não encontrada"):
        service.get_ship_available_capacity(999)