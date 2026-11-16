from copy import deepcopy
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.repositories import memory
from backend.schemas.mission import MissionCreate
from backend.schemas.mission_ship import MissionShipCreate, MissionShipResponse
from backend.schemas.ship import ShipCreate
from backend.services import mission, mission_event, mission_ship, rescue_request, ship, strategy

@pytest.fixture(autouse=True)
def isolated_repositories():
    def clear():
        with memory.lock:
            for repository in (memory.missions, memory.ships, memory.mission_ships,
                               memory.requests, memory.events):
                repository.clear()
            for key in memory.counters:
                memory.counters[key] = 0

    clear()
    try:
        yield
    finally:
        clear()

@pytest.fixture(autouse=True)
def clock(monkeypatch):
    class FixedDateTime(datetime):
        current = datetime(2030, 1, 1, 12, tzinfo=timezone.utc)

        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return cls.current.replace(tzinfo=None)
            return cls.current.astimezone(tz)

    for module in (mission, mission_event, rescue_request, strategy):
        monkeypatch.setattr(module, "datetime", FixedDateTime)
    return FixedDateTime

@pytest.fixture
def now(clock):
    return clock.current

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def make_mission():
    def create(people=10, urgency="MEDIUM", name="Resgate Aurora", created_at=None):
        result = mission.create_mission(MissionCreate(
            name=name, station="Aurora", people_count=people, urgency=urgency
        ))
        if created_at is not None:
            result["created_at"] = created_at
        return result
    return create

@pytest.fixture
def make_ship():
    def create(capacity=10, name="Nave de teste"):
        return ship.create_ship(ShipCreate(name=name, total_capacity=capacity))
    return create

@pytest.fixture
def make_offer(now):
    def create(mission, ship, seats=None, eta=30, automatic=False):
        data = MissionShipCreate(
            mission_id=mission["id"], ship_id=ship["id"],
            offered_seats=ship["total_capacity"] if seats is None else seats,
            arrival_time=now + timedelta(minutes=eta),
        )
        if automatic:
            return mission_ship.offer_ship(**data.model_dump())
        with memory.lock:
            offer = MissionShipResponse(
                id=memory.generate_id("mission_ships"), **data.model_dump(),
                ship_name=ship["name"], status="AVAILABLE",
            ).model_dump()
            memory.mission_ships[offer["id"]] = offer
        return offer
    return create

@pytest.fixture
def pending_request(make_mission, make_ship, make_offer):
    def create(people=10, seats=5, capacity=10, expires_at=None, urgency="MEDIUM"):
        target = make_mission(people=people, urgency=urgency)
        vessel = make_ship(capacity=capacity)
        offer = make_offer(target, vessel, seats=seats)
        request = rescue_request.create_request(
            target["id"], offer["id"], seats, expires_at=expires_at
        )
        return target, vessel, offer, request
    return create

@pytest.fixture
def snapshot():
    def capture():
        with memory.lock:
            return deepcopy({name: getattr(memory, name) for name in
                             ("missions", "ships", "mission_ships", "requests",
                              "events", "counters")})
    return capture

@pytest.fixture
def run_concurrently():
    def run(first, second):
        barrier = Barrier(2, timeout=5)

        def invoke(operation):
            barrier.wait()
            try:
                return "ok", deepcopy(operation())
            except ValueError as error:
                return "rejected", str(error)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(invoke, operation) for operation in (first, second)]
            return [future.result(timeout=10) for future in futures]
    return run