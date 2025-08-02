from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.room import Room
from app.schemas.room_schema import room_schema, rooms_schema
from app.schemas.room_create_schema import RoomCreateSchema
from app.db import db

room_bp = Blueprint('room_bp', __name__, url_prefix='/api/admin/rooms')

# GET all rooms
@room_bp.route('', methods=['GET'])
def get_all_rooms():
    rooms = Room.query.all()
    return jsonify(rooms_schema.dump(rooms)), 200

# GET room by ID
@room_bp.route('/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'message': 'Room not found'}), 404
    return jsonify(room_schema.dump(room)), 200

# POST create new room
@room_bp.route('', methods=['POST'])
def create_room():
    data = request.get_json()
    print("Incoming data:", data)  # Debug: Print the incoming request payload

    schema = RoomCreateSchema()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        print("Validation errors:", err.messages)  # Debug: print validation errors
        return jsonify({"errors": err.messages}), 422

    new_room = Room(**validated)

    db.session.add(new_room)
    db.session.commit()

    return jsonify(room_schema.dump(new_room)), 201
