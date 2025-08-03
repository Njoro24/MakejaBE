from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.room import Room
from app.schemas.room_schema import RoomSchema
from app.schemas.room_create_schema import RoomCreateSchema
from app.db import db

room_bp = Blueprint('room', __name__, url_prefix='/api/rooms')

room_schema = RoomSchema()
room_create_schema = RoomCreateSchema()

@room_bp.route('', methods=['POST'])
@jwt_required()
def create_room():
    user_id = get_jwt_identity()
    data = request.get_json()

    errors = room_create_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    room = Room(
        title=data['title'],
        location=data['location'],
        description=data['description'],
        price_per_night=data['price_per_night'],
        capacity=data['capacity'],
        category=data['category'],
        image=data['image'],
        host_id=user_id
    )

    db.session.add(room)
    db.session.commit()

    return room_schema.dump(room), 201
