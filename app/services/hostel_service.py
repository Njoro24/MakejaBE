from app.models.hostel import Hostel
from app.extensions import db


def create_hostel(data, owner_id):
    new_hostel = Hostel(
        name=data["name"],
        location=data["location"],
        price_per_month=data["price_per_month"],
        description=data.get("description"),
        amenities=data.get("amenities"),
        photos=data.get("photos"),
        owner_id=owner_id
    )
    db.session.add(new_hostel)
    db.session.commit()
    return new_hostel


def get_all_hostels():
    return Hostel.query.all()


def get_hostel_by_id(hostel_id):
    return Hostel.query.get(hostel_id)


def update_hostel(hostel_id, data):
    hostel = get_hostel_by_id(hostel_id)
    if not hostel:
        return None

    for key, value in data.items():
        setattr(hostel, key, value)

    db.session.commit()
    return hostel


def delete_hostel(hostel_id):
    hostel = get_hostel_by_id(hostel_id)
    if hostel:
        db.session.delete(hostel)
        db.session.commit()
