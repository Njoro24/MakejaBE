

import pytest
from flask import url_for
from app import create_app
from app.extensions import db
from app.models.hostel import Hostel
from app.models.user import User
from flask_jwt_extended import create_access_token


@pytest.fixture(scope="session")
def test_app():
    app = create_app("testing") 
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


@pytest.fixture
def owner_user(test_app):
    user = User(username="owner", email="owner@example.com", role="user")
    user.set_password("password")  # assuming User model has set_password
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(test_app):
    admin = User(username="admin", email="admin@example.com", role="admin")
    admin.set_password("password")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def other_user(test_app):
    user = User(username="other", email="other@example.com", role="user")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    return user


def auth_headers(user):
    token = create_access_token(identity=user.id)
    return {"Authorization": f"Bearer {token}"}


def test_create_hostel_as_owner(client, owner_user):
    payload = {
        "name": "Test Hostel",
        "location": "Ruiru",
        "price": 1500.0,
        "description": "Nice place",
        "amenities": ["wifi", "laundry"],
        "available": True
    }

    res = client.post(
        "/api/hostels/",
        json=payload,
        headers=auth_headers(owner_user)
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "Test Hostel"
    assert data["location"] == "Ruiru"
    assert data["owner_id"] == owner_user.id


def test_list_hostels(client, owner_user):
    # Ensure at least one hostel exists
    payload = {
        "name": "List Hostel",
        "location": "Nairobi",
        "price": 2000.0,
        "description": "Listed place",
        "amenities": ["wifi"],
        "available": True
    }
    client.post("/api/hostels/", json=payload, headers=auth_headers(owner_user))

    res = client.get("/api/hostels/")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert any(h["name"] == "List Hostel" for h in data)


def test_retrieve_hostel(client, owner_user):
    payload = {
        "name": "Retrieve Hostel",
        "location": "Kiambu",
        "price": 1200.0,
        "description": "Retrieve place",
        "amenities": [],
        "available": True
    }
    create_res = client.post("/api/hostels/", json=payload, headers=auth_headers(owner_user))
    hostel_id = create_res.get_json()["id"]

    res = client.get(f"/api/hostels/{hostel_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == hostel_id
    assert data["name"] == "Retrieve Hostel"


def test_update_hostel_not_owner_forbidden(client, owner_user, other_user):
    # Owner creates
    payload = {
        "name": "Owner Hostel",
        "location": "Ruiru",
        "price": 3000.0,
        "description": "Original",
        "amenities": [],
        "available": True
    }
    create_res = client.post("/api/hostels/", json=payload, headers=auth_headers(owner_user))
    hostel_id = create_res.get_json()["id"]

    # Other user tries update
    update_payload = {"description": "Hacked"}
    res = client.patch(
        f"/api/hostels/{hostel_id}",
        json=update_payload,
        headers=auth_headers(other_user)
    )
    assert res.status_code == 403
    assert "Not authorized" in res.get_json().get("error", "")


def test_update_hostel_as_owner(client, owner_user):
    payload = {
        "name": "Owner Update Hostel",
        "location": "Ruiru",
        "price": 2500.0,
        "description": "Before",
        "amenities": [],
        "available": True
    }
    create_res = client.post("/api/hostels/", json=payload, headers=auth_headers(owner_user))
    hostel_id = create_res.get_json()["id"]

    update_payload = {"description": "After"}
    res = client.patch(
        f"/api/hostels/{hostel_id}",
        json=update_payload,
        headers=auth_headers(owner_user)
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["description"] == "After"


def test_update_hostel_as_admin(client, owner_user, admin_user):
    payload = {
        "name": "Admin Update Hostel",
        "location": "Ruiru",
        "price": 2200.0,
        "description": "Before admin",
        "amenities": [],
        "available": True
    }
    create_res = client.post("/api/hostels/", json=payload, headers=auth_headers(owner_user))
    hostel_id = create_res.get_json()["id"]

    update_payload = {"description": "Admin changed"}
    res = client.patch(
        f"/api/hostels/{hostel_id}",
        json=update_payload,
        headers=auth_headers(admin_user)
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["description"] == "Admin changed"


def test_delete_hostel_not_owner_forbidden(client, owner_user, other_user):
    payload = {
        "name": "Delete Hostel",
        "location": "Ruiru",
        "price": 1800.0,
        "description": "To be deleted",
        "amenities": [],
        "available": True
    }
    create_res = client.post("/api/hostels/", json=payload, headers=auth_headers(owner_user))
    hostel_id = create_res.get_json()["id"]

    res = client.delete(f"/api/hostels/{hostel_id}", headers=auth_headers(other_user))
    assert res.status_code == 403


def test_delete_hostel_as_owner(client, owner_user):
    payload = {
        "name": "Delete Owned Hostel",
        "location": "Ruiru",
        "price": 1900.0,
        "description": "To be deleted",
        "amenities": [],
        "available": True
    }
    create_res = client.post("/api/hostels/", json=payload, headers=auth_headers(owner_user))
    hostel_id = create_res.get_json()["id"]

    res = client.delete(f"/api/hostels/{hostel_id}", headers=auth_headers(owner_user))
    assert res.status_code == 200
    # Ensure it's gone
    get_res = client.get(f"/api/hostels/{hostel_id}")
    assert get_res.status_code == 404
