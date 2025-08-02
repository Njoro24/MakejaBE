from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.models.room import Room
from app.db import db
from app.schemas.room_create_schema import RoomCreateSchema

admin_bp = Blueprint('admin_bp', __name__)
room_create_schema = RoomCreateSchema()

@admin_bp.route('/rooms', methods=['POST'])
@jwt_required()
def create_room_admin():
    current_user_id = get_jwt_identity()

    try:
        data = request.get_json()
        print("🔥 INCOMING ROOM DATA:", data)

        if not data:
            raise ValueError("❌ No JSON payload received. Check Content-Type or frontend code.")

        data['host_id'] = current_user_id

        validated_data = room_create_schema.load(data)
        print("✅ VALIDATED DATA:", validated_data)

        room = Room(**validated_data)
        db.session.add(room)
        db.session.commit()

        return jsonify({'message': 'Room created successfully', 'room_id': room.id}), 201

    except ValidationError as err:
        print("❌ VALIDATION ERROR:", err.messages)
        return jsonify({
            "error": "Validation failed",
            "missing_fields": list(err.messages.keys()),
            "details": err.messages
        }), 422

    except Exception as e:
        print("💥 SERVER ERROR:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
