from app.models.hostel import Hostel
from app.extensions import db


def create_hostel(data, owner_id):
    hostel = Hostel(
        name=data["name"],
        location=data["location"],
        price=data["price"],
        description=data.get("description", ""),
        amenities=data.get("amenities", []),
        available=data.get("available", True),
        owner_id=owner_id
    )
    db.session.add(hostel)
    db.session.commit()
    return hostel


def get_all_hostels():
    return Hostel.query.all()


def get_hostel_by_id(hostel_id):
    return Hostel.query.get(hostel_id)


def update_hostel(hostel_id, data):
    hostel = Hostel.query.get(hostel_id)
    if not hostel:
        return None

    for key, value in data.items():
        setattr(hostel, key, value)

    db.session.commit()
    return hostel


def delete_hostel(hostel_id):
    hostel = Hostel.query.get(hostel_id)
    if hostel:
        db.session.delete(hostel)
        db.session.commit()
