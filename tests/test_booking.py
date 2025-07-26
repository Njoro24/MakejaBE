import requests

BASE_URL = "http://127.0.0.1:5000"

def test_booking_flow():
    # Step 1: Register user (skip if already exists)
    register_payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    }
    requests.post(f"{BASE_URL}/auth/register", json=register_payload)

    # Step 2: Login
    login_payload = {
        "email": "test@example.com",
        "password": "123456"
    }
    login_resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 3: Create room (if you have admin protection, use admin token instead)
    room_payload = {
        "name": "Test Room",
        "description": "A simple test room",
        "price_per_night": 1000
    }
    room_resp = requests.post(f"{BASE_URL}/rooms", json=room_payload, headers=headers)
    assert room_resp.status_code in [200, 201], f"Room creation failed: {room_resp.text}"
    room_id = room_resp.json()["id"]

    # Step 4: Book room
    booking_payload = {
        "room_id": room_id,
        "check_in_date": "2025-08-01",
        "check_out_date": "2025-08-07"
    }
    booking_resp = requests.post(f"{BASE_URL}/bookings", json=booking_payload, headers=headers)
    assert booking_resp.status_code == 201, f"Booking failed: {booking_resp.text}"

    # Step 5: Fetch bookings
    get_resp = requests.get(f"{BASE_URL}/bookings", headers=headers)
    assert get_resp.status_code == 200, f"Fetching bookings failed: {get_resp.text}"
    print("✔ Booking flow test passed successfully")

if __name__ == "__main__":
    test_booking_flow()
