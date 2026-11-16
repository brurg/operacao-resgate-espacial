import pytest
from backend.repositories import memory
from backend.services import rescue_request as rescue
from backend.services import strategy

@pytest.mark.parametrize("attempt", range(5))
def test_two_missions_cannot_overcommit_one_ship(make_mission, make_ship, make_offer, run_concurrently, attempt):
    targets = [make_mission(people=6), make_mission(people=6)]
    vessel = make_ship(capacity=10)
    offers = [make_offer(target, vessel, seats=6) for target in targets]
    outcomes = run_concurrently(
        lambda: rescue.create_request(targets[0]["id"], offers[0]["id"], 6),
        lambda: rescue.create_request(targets[1]["id"], offers[1]["id"], 6),
    )
    assert sorted(status for status, _ in outcomes) == ["ok", "rejected"]
    assert len(memory.requests) == 1
    assert rescue.get_ship_committed_seats(vessel["id"]) == 6
    assert rescue.get_ship_available_capacity(vessel["id"]) == 4

@pytest.mark.parametrize("attempt", range(5))
def test_two_offers_cannot_overcommit_one_mission(make_mission, make_ship, make_offer, run_concurrently, attempt):
    target = make_mission(people=5)
    offers = [make_offer(target, make_ship(capacity=5)) for _ in range(2)]
    outcomes = run_concurrently(
        lambda: rescue.create_request(target["id"], offers[0]["id"], 5),
        lambda: rescue.create_request(target["id"], offers[1]["id"], 5),
    )
    assert sorted(status for status, _ in outcomes) == ["ok", "rejected"]
    summary = rescue.get_mission_seat_summary(target["id"])
    assert summary["pending_seats"] == 5
    assert summary["uncommitted_seats"] == 0
    assert len(memory.requests) == 1

@pytest.mark.parametrize("attempt", range(5))
def test_simultaneous_duplicate_responses_count_once(pending_request, run_concurrently, attempt):
    target, _, _, request = pending_request(people=5, seats=5)
    outcomes = run_concurrently(
        lambda: rescue.register_response(request["id"], 5),
        lambda: rescue.register_response(request["id"], 5),
    )
    assert sorted(status for status, _ in outcomes) == ["ok", "rejected"]
    assert request["status"] == "CONFIRMED"
    assert rescue.get_mission_seat_summary(target["id"])["confirmed_seats"] == 5
    assert len([e for e in memory.events.values() if e["event_type"] == "REQUEST_RESPONDED"]) == 1
    assert len([e for e in memory.events.values() if e["event_type"] == "MISSION_COMPLETED"]) == 1

@pytest.mark.parametrize("attempt", range(5))
def test_responses_to_different_requests_cannot_exceed_need(make_mission, make_ship, make_offer, run_concurrently, attempt):
    target = make_mission(people=10)
    offers = [make_offer(target, make_ship(capacity=5)) for _ in range(2)]
    requests = [rescue.create_request(target["id"], offer["id"], 5) for offer in offers]
    outcomes = run_concurrently(
        lambda: rescue.register_response(requests[0]["id"], 5),
        lambda: rescue.register_response(requests[1]["id"], 5),
    )
    assert [status for status, _ in outcomes] == ["ok", "ok"]
    assert rescue.get_mission_seat_summary(target["id"]) == {
        "people_count": 10, "confirmed_seats": 10, "pending_seats": 0,
        "missing_seats": 0, "uncommitted_seats": 0,
    }
    assert target["status"] == "COMPLETED"
    assert len([e for e in memory.events.values() if e["event_type"] == "MISSION_COMPLETED"]) == 1

@pytest.mark.parametrize("competing", ["partial", "refuse", "cancel", "expire"])
@pytest.mark.parametrize("attempt", range(5))
def test_terminal_decision_cannot_be_overwritten_by_racing_response(pending_request, now, run_concurrently, competing, attempt):
    target, _, _, request = pending_request(people=5, seats=5, expires_at=now)

    def competing_operation():
        if competing == "partial":
            return rescue.register_response(request["id"], 2)
        if competing == "refuse":
            return rescue.register_response(request["id"], 0)
        if competing == "cancel":
            return rescue.cancel_request(request["id"])
        return rescue.expire_request(request["id"])

    outcomes = run_concurrently(
        lambda: rescue.register_response(request["id"], 5), competing_operation
    )
    assert sorted(status for status, _ in outcomes) == ["ok", "rejected"]
    winner = next(result for status, result in outcomes if status == "ok")
    assert request == winner
    assert request["status"] in {"CONFIRMED", {"partial": "PARTIAL", "refuse": "UNAVAILABLE",
                                              "cancel": "CANCELLED", "expire": "EXPIRED"}[competing]}
    summary = rescue.get_mission_seat_summary(target["id"])
    assert summary["confirmed_seats"] == winner["confirmed_seats"]
    assert summary["pending_seats"] == 0
    assert summary["confirmed_seats"] <= target["people_count"]

@pytest.mark.parametrize("attempt", range(5))
def test_parallel_strategy_calls_do_not_duplicate_requests(make_mission, make_ship, make_offer, run_concurrently, attempt):
    target = make_mission(people=5)
    make_offer(target, make_ship(capacity=5))
    outcomes = run_concurrently(strategy.execute_strategy, strategy.execute_strategy)
    assert [status for status, _ in outcomes] == ["ok", "ok"]
    assert sorted(len(result) for _, result in outcomes) == [0, 1]
    assert len(memory.requests) == 1
    assert rescue.get_mission_seat_summary(target["id"])["pending_seats"] == 5