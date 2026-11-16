from datetime import timedelta
import pytest
from backend.repositories import memory
from backend.services import rescue_request as rescue
from backend.services import strategy

@pytest.mark.parametrize("urgency,expected", [("HIGH", [2, 3, 1]), ("MEDIUM", [3, 1, 2]), ("LOW", [1, 3, 2])])
def test_ranking_with_uncommitted_capacity(make_mission, make_ship, make_offer, urgency, expected):
    target = make_mission(urgency=urgency)
    offers = [make_offer(target, make_ship(capacity=capacity), eta=eta)
              for capacity, eta in [(10, 180), (4, 0), (8, 30)]]
    ranked = strategy.rank_offers(offers, urgency)
    assert [item["offer"]["id"] for item in ranked] == expected

def test_medium_score_uses_exact_half_time_half_capacity(make_mission, make_ship, make_offer):
    target = make_mission()
    offers = [make_offer(target, make_ship(capacity=capacity), eta=eta)
              for capacity, eta in [(10, 180), (4, 0), (8, 30)]]
    ranked = strategy.rank_offers(offers, "MEDIUM")
    expected_scores = {
        offers[0]["id"]: 0.75,
        offers[1]["id"]: 0.70,
        offers[2]["id"]: 0.5 * (6 / 7) + 0.5 * 0.8,
    }
    for item in ranked:
        assert item["score"] == pytest.approx(expected_scores[item["offer"]["id"]])

@pytest.mark.parametrize("urgency,capacities,etas,expected", [
    ("HIGH", [4, 8, 6], [30, 30, 60], [2, 1, 3]),
    ("LOW", [8, 8, 4], [60, 30, 0], [2, 1, 3]),
    ("MEDIUM", [4, 2], [180, 0], [2, 1]),
])
def test_ranking_tiebreakers(make_mission, make_ship, make_offer,
                            urgency, capacities, etas, expected):
    target = make_mission(urgency=urgency)
    offers = [make_offer(target, make_ship(capacity=c), eta=t)
              for c, t in zip(capacities, etas)]
    assert [item["offer"]["id"] for item in strategy.rank_offers(offers, urgency)] == expected

@pytest.mark.parametrize("urgency", ["HIGH", "MEDIUM", "LOW"])
def test_strategy_selects_best_ship_before_creating_requests(make_mission, make_ship,
                                                           make_offer, urgency):
    target = make_mission(people=3, urgency=urgency)
    offers = [make_offer(target, make_ship(capacity=c), eta=t)
              for c, t in [(10, 180), (4, 0), (8, 30)]]
    best_index = {"HIGH": 1, "MEDIUM": 2, "LOW": 0}[urgency]
    result = strategy.execute_strategy()
    assert len(memory.requests) == 1
    request = next(iter(memory.requests.values()))
    assert request["mission_ship_id"] == offers[best_index]["id"]
    assert request["requested_seats"] == 3
    assert result[0]["uncommitted_seats_remaining"] == 0

@pytest.mark.parametrize("trigger", [None, "low"])
def test_global_priority_high_medium_low_even_with_targeted_call(make_mission, make_ship, make_offer, now, trigger):
    low = make_mission(people=4, urgency="LOW", created_at=now - timedelta(days=3))
    medium = make_mission(people=4, urgency="MEDIUM", created_at=now - timedelta(days=2))
    high = make_mission(people=4, urgency="HIGH", created_at=now)
    vessel = make_ship(capacity=10)
    for target in (low, medium, high):
        make_offer(target, vessel, seats=4)
    result = strategy.execute_strategy(low["id"] if trigger else None)
    assert [r["mission_id"] for r in result] == [high["id"], medium["id"], low["id"]]
    assert [(r["mission_id"], r["requested_seats"]) for r in memory.requests.values()] == [
        (high["id"], 4), (medium["id"], 4), (low["id"], 2),
    ]

@pytest.mark.parametrize("urgency", ["HIGH", "MEDIUM", "LOW"])
def test_same_urgency_uses_creation_time_not_insertion_order(make_mission, make_ship, make_offer, now, urgency):
    newer = make_mission(people=4, urgency=urgency, created_at=now)
    older = make_mission(people=4, urgency=urgency, created_at=now - timedelta(hours=1))
    vessel = make_ship(capacity=5)
    for target in (newer, older):
        make_offer(target, vessel, seats=4)
    result = strategy.execute_strategy(newer["id"])
    assert [r["mission_id"] for r in result] == [older["id"], newer["id"]]
    assert [r["requested_seats"] for r in memory.requests.values()] == [4, 1]

@pytest.mark.parametrize("operation", ["partial", "refuse", "cancel", "expire"])
def test_local_request_change_rechecks_global_priority(make_mission, make_ship, make_offer, now, operation):
    low = make_mission(people=5, urgency="LOW")
    high = make_mission(people=5, urgency="HIGH")
    vessel = make_ship(capacity=5)
    low_offer = make_offer(low, vessel)
    low_request = rescue.create_request(low["id"], low_offer["id"], 5, expires_at=now)
    high_offer = make_offer(high, vessel)
    if operation == "partial":
        rescue.register_response(low_request["id"], 2)
    elif operation == "refuse":
        rescue.register_response(low_request["id"], 0)
    elif operation == "cancel":
        rescue.cancel_request(low_request["id"])
    else:
        rescue.expire_request(low_request["id"])
    high_requests = rescue.list_requests(high["id"])
    assert len(high_requests) == 1
    assert high_requests[0]["mission_ship_id"] == high_offer["id"]
    assert high_requests[0]["requested_seats"] == (3 if operation == "partial" else 5)
    assert rescue.get_ship_committed_seats(vessel["id"]) == 5

@pytest.mark.parametrize("need,offered,capacity,committed,expected", [
    (3, 8, 10, 0, 3), (10, 4, 10, 0, 4), (10, 10, 10, 7, 3),
    (4, 4, 4, 0, 4), (10, 10, 10, 10, 0),
])
def test_allocation_is_minimum_of_need_offer_and_available_capacity(make_mission, make_ship, make_offer, need, offered, capacity, committed, expected):
    blocker = make_mission(people=capacity, urgency="HIGH")
    target = make_mission(people=need, urgency="LOW")
    vessel = make_ship(capacity=capacity)
    if committed:
        offer = make_offer(blocker, vessel)
        request = rescue.create_request(blocker["id"], offer["id"], committed)
        rescue.register_response(request["id"], committed)
    make_offer(target, vessel, seats=offered)
    strategy.execute_strategy()
    assert sum(r["requested_seats"] for r in rescue.list_requests(target["id"])) == expected
    assert rescue.get_ship_committed_seats(vessel["id"]) == committed + expected

def test_confirmed_and_pending_seats_prevent_duplicate_mobilization(make_mission, make_ship, make_offer, snapshot):
    target = make_mission(people=10)
    first = make_offer(target, make_ship(capacity=4))
    confirmed = rescue.create_request(target["id"], first["id"], 4)
    rescue.register_response(confirmed["id"], 4)
    second = make_offer(target, make_ship(capacity=6))
    rescue.create_request(target["id"], second["id"], 6)
    spare = make_offer(target, make_ship(capacity=10))
    before = snapshot()
    assert strategy.execute_strategy() == []
    assert strategy.execute_strategy(target["id"]) == []
    assert snapshot() == before
    assert spare["status"] == "AVAILABLE"
    assert rescue.get_mission_seat_summary(target["id"]) == {
        "people_count": 10, "confirmed_seats": 4, "pending_seats": 6,
        "missing_seats": 6, "uncommitted_seats": 0,
    }
    assert target["status"] == "IN_PROGRESS"

def test_completed_mission_never_mobilizes_spare_offer(pending_request, make_ship, make_offer, snapshot):
    target, _, _, request = pending_request(people=5, seats=5)
    spare = make_offer(target, make_ship())
    rescue.register_response(request["id"], 5)
    before = snapshot()
    assert strategy.execute_strategy() == []
    assert snapshot() == before
    assert spare["status"] == "AVAILABLE"

@pytest.mark.parametrize("operation,confirmed,expected", [
    ("partial", 2, 3), ("refuse", 0, 5), ("cancel", 0, 5), ("expire", 0, 5),
])
def test_unfulfilled_seats_generate_new_request_automatically(
        pending_request, make_ship, make_offer, now, operation, confirmed, expected):
    target, original_ship, original_offer, request = pending_request(
        people=5, seats=5, expires_at=now
    )
    replacement = make_offer(target, make_ship(capacity=10))
    if operation in ("partial", "refuse"):
        rescue.register_response(request["id"], confirmed)
    elif operation == "cancel":
        rescue.cancel_request(request["id"])
    else:
        rescue.expire_request(request["id"])
    requests = rescue.list_requests(target["id"])
    assert len(requests) == 2
    assert requests[1]["mission_ship_id"] == replacement["id"]
    assert requests[1]["requested_seats"] == expected
    assert requests[1]["status"] == "PENDING"
    assert original_offer["status"] == "UNAVAILABLE"
    assert rescue.get_ship_available_capacity(original_ship["id"]) == 10 - confirmed
    summary = rescue.get_mission_seat_summary(target["id"])
    assert summary["confirmed_seats"] == confirmed
    assert summary["pending_seats"] == expected
    assert summary["uncommitted_seats"] == 0

def test_released_capacity_can_serve_another_mission(pending_request, make_mission, make_offer):
    first, vessel, _, request = pending_request(people=5, seats=5, capacity=5)
    second = make_mission(people=5)
    make_offer(second, vessel)
    rescue.register_response(request["id"], 2)
    second_requests = rescue.list_requests(second["id"])
    assert len(second_requests) == 1
    assert second_requests[0]["requested_seats"] == 3
    assert rescue.get_mission_seat_summary(first["id"])["uncommitted_seats"] == 3
    assert rescue.get_ship_available_capacity(vessel["id"]) == 0

def test_new_high_offer_reallocates_lower_pending_request(make_mission, make_ship, make_offer):
    low = make_mission(people=5, urgency="LOW")
    high = make_mission(people=5, urgency="HIGH")
    vessel = make_ship(capacity=5)
    low_offer = make_offer(low, vessel, automatic=True)
    old_request = rescue.list_requests(low["id"])[0]
    high_offer = make_offer(high, vessel, automatic=True)
    updated_request = rescue.get_request(old_request["id"])
    assert updated_request["status"] == "CANCELLED"
    assert low_offer["status"] == "AVAILABLE"
    assert rescue.list_requests(high["id"])[0]["mission_ship_id"] == high_offer["id"]
    assert rescue.get_ship_committed_seats(vessel["id"]) == 5
    events = [e for e in memory.events.values() if e["event_type"] == "REQUEST_CANCELLED"]
    assert len(events) == 1
    assert events[0]["details"]["automatic_reallocation"] is True
    assert events[0]["details"]["higher_priority_mission_id"] == high["id"]

@pytest.mark.parametrize("required,expected_indices", [(3, [2]), (5, [2, 1]), (8, [2, 1, 0])])
def test_reallocation_releases_lowest_priority_and_newest_first(
        make_mission, make_ship, make_offer, clock, required, expected_indices):
    high = make_mission(urgency="HIGH")
    others = [make_mission(urgency=urgency) for urgency in ("MEDIUM", "LOW", "LOW")]
    vessel = make_ship(capacity=10)
    requests = []
    for target, seats in zip(others, (4, 3, 3)):
        clock.current += timedelta(minutes=1)
        offer = make_offer(target, vessel, seats=seats)
        requests.append(rescue.create_request(target["id"], offer["id"], seats))
    cancelled = strategy.release_lower_priority_requests(vessel["id"], high, required)
    assert cancelled == [requests[index]["id"] for index in expected_indices]
    for index, request in enumerate(requests):
        assert request["status"] == ("CANCELLED" if index in expected_indices else "PENDING")

@pytest.mark.parametrize("state,urgency,confirmed,expected", [
    ("PENDING", "HIGH", None, 2),
    ("CONFIRMED", "LOW", 8, 2),
    ("PARTIAL", "LOW", 6, 4),
])
def test_reallocation_preserves_equal_priority_and_received_confirmations(
        make_mission, make_ship, make_offer, state, urgency, confirmed, expected):
    blocker = make_mission(people=10, urgency=urgency)
    high = make_mission(people=5, urgency="HIGH")
    vessel = make_ship(capacity=10)
    offer = make_offer(blocker, vessel, seats=8)
    previous = rescue.create_request(blocker["id"], offer["id"], 8)
    if confirmed is not None:
        rescue.register_response(previous["id"], confirmed)
    make_offer(high, vessel, seats=5)
    strategy.execute_strategy()
    assert previous["status"] == state
    assert rescue.list_requests(high["id"])[0]["requested_seats"] == expected
    assert rescue.get_ship_committed_seats(vessel["id"]) == 10

def test_rescue_scenario_partial_refusal_and_recovery_to_completion(
        make_mission, make_ship, make_offer):
    target = make_mission(people=10, urgency="HIGH")
    offers = [make_offer(target, make_ship(capacity=c), eta=t)
              for c, t in [(6, 10), (4, 20), (10, 30)]]
    strategy.execute_strategy()
    first, second = rescue.list_requests(target["id"])
    assert [first["requested_seats"], second["requested_seats"]] == [6, 4]
    rescue.register_response(first["id"], 3)
    third = rescue.list_requests(target["id"])[2]
    assert third["mission_ship_id"] == offers[2]["id"]
    assert third["requested_seats"] == 3
    rescue.register_response(second["id"], 0)
    assert rescue.get_mission_seat_summary(target["id"])["uncommitted_seats"] == 4
    fourth_offer = make_offer(target, make_ship(capacity=4), eta=40, automatic=True)
    fourth = rescue.list_requests(target["id"])[3]
    assert fourth["mission_ship_id"] == fourth_offer["id"]
    assert fourth["requested_seats"] == 4
    rescue.register_response(third["id"], 3)
    assert target["status"] == "IN_PROGRESS"
    rescue.register_response(fourth["id"], 4)
    assert target["status"] == "COMPLETED"
    assert rescue.get_mission_seat_summary(target["id"]) == {
        "people_count": 10, "confirmed_seats": 10, "pending_seats": 0,
        "missing_seats": 0, "uncommitted_seats": 0,
    }

@pytest.mark.parametrize("value,minutes", [
    ("2030-01-01T13:00:00Z", 60),
    ("2030-01-01T10:00:00-03:00", 60),
    ("2030-01-01T13:00:00", 60),
    ("2030-01-01T11:00:00Z", 0),
    ("2030-01-01T18:00:00Z", 360),
])
def test_eta_timezone_past_and_no_hard_180_minute_limit(value, minutes):
    assert strategy.get_eta_minutes(value) == minutes

@pytest.mark.parametrize("urgency", ["HIGH", "MEDIUM", "LOW"])
def test_ranking_uses_available_capacity_instead_of_original_offer(
        make_mission, make_ship, make_offer, urgency):
    """Regressão: atualmente falha porque rank_offers usa offered_seats.

    A oferece 10, mas já confirmou 9 em outra missão; só tem 1 livre.
    B oferece 8 e tem 8 livres. ETA igual: B deve atender as 5 pessoas.
    O bloqueio confirmado impede que a realocação mascare a divergência.
    """
    blocker = make_mission(people=9, urgency="HIGH")
    ship_a = make_ship(capacity=10, name="A: apenas um livre")
    blocker_offer = make_offer(blocker, ship_a, seats=9)
    committed = rescue.create_request(blocker["id"], blocker_offer["id"], 9)
    rescue.register_response(committed["id"], 9)
    target = make_mission(people=5, urgency=urgency)
    make_offer(target, ship_a, seats=10, eta=30)
    ship_b = make_ship(capacity=8, name="B: oito livres")
    best_offer = make_offer(target, ship_b, seats=8, eta=30)
    assert rescue.get_ship_available_capacity(ship_a["id"]) == 1
    assert rescue.get_ship_available_capacity(ship_b["id"]) == 8
    strategy.execute_strategy()
    actual = [(r["mission_ship_id"], r["requested_seats"])
              for r in rescue.list_requests(target["id"])]
    assert actual == [(best_offer["id"], 5)], (
        "A classificação deve considerar a capacidade livre: B sozinha atende 5; "
        f"pedidos criados (oferta, assentos): {actual}"
    )
