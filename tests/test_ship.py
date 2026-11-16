import pytest

def test_register_valid_ship(client):
    response = client.post("/ships/", json={"name": "Explorer", "total_capacity": 12})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Explorer", "total_capacity": 12}

@pytest.mark.parametrize("capacity", [0, -1, -100, 2.5, "inválido", None])
def test_invalid_capacity_rejected(client, snapshot, capacity):
    before = snapshot()
    response = client.post("/ships/", json={"name": "Explorer", "total_capacity": capacity})
    assert response.status_code == 422
    assert snapshot() == before

def test_list_get_and_missing_ship(client, make_ship):
    response = client.get("/ships/")
    assert response.status_code == 200
    assert response.json() == []
    vessels = [make_ship(capacity=5), make_ship(capacity=12)]
    listing = client.get("/ships/")
    assert listing.status_code == 200
    assert listing.json() == vessels
    for vessel in vessels:
        result = client.get(f"/ships/{vessel['id']}")
        assert result.status_code == 200
        assert result.json() == vessel
    assert client.get("/ships/999").status_code == 404