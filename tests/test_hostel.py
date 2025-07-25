# tests/test_hostel.py

import json

def test_create_hostel(client, db_session, test_user):
    # Simulate logged-in user as host
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    payload = {
        "name": "Sunshine Hostel",
        "description": "A clean and affordable place for students.",
        "location": "Nairobi",
        "price_per_night": 1000,
        "amenities": ["Wi-Fi", "Hot Shower", "Security"],
        "host_id": test_user["user"]["id"]
    }

    response = client.post("/api/hostels", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Sunshine Hostel"
    assert "id" in data

def test_get_hostels(client, db_session):
    response = client.get("/api/hostels")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_single_hostel(client, db_session, created_hostel):
    response = client.get(f"/api/hostels/{created_hostel.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == created_hostel.id

def test_update_hostel(client, db_session, created_hostel, test_user):
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    payload = {"price_per_night": 1200}
    response = client.put(f"/api/hostels/{created_hostel.id}", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["price_per_night"] == 1200

def test_delete_hostel(client, db_session, created_hostel, test_user):
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.delete(f"/api/hostels/{created_hostel.id}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Hostel deleted"
