from app.models.room import Room
from app.db import db

def create_room(data, host_id):
    room = Room(**data, host_id=host_id)
    db.session.add(room)
    db.session.commit()
    return room

def get_rooms_by_host(host_id):
    return Room.query.filter_by(host_id=host_id).all()
