from flask import Blueprint, jsonify
from app.models import Room

room_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

@room_bp.route('/', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    result = [
        {
            'id': room.id,
            'name': room.name,
            'price_per_night': room.price_per_night
        } for room in rooms
    ]
    return jsonify(result)
