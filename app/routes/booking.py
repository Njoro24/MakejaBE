from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.booking import Booking
from app.models.user import User
from app.models.room import Room

booking_bp = Blueprint("booking", __name__, url_prefix="/api/bookings")

@booking_bp.route("/", methods=["POST"])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    print("JWT Identity (User ID):", user_id)  # Debug print

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role != "user":
        return jsonify({"error": "Only users can create bookings"}), 403

    data = request.get_json()
    room_id = data.get("room_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not room_id or not start_date or not end_date:
        return jsonify({"error": "Missing required fields"}), 400

    room = Room.query.get(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    if room.host_id == user_id:
        return jsonify({"error": "You cannot book your own room"}), 403

    new_booking = Booking(
        user_id=user_id,
        room_id=room_id,
        start_date=start_date,
        end_date=end_date
    )

    db.session.add(new_booking)
    db.session.commit()

    return jsonify({
        "message": "Booking created successfully",
        "booking": {
            "id": new_booking.id,
            "room_id": new_booking.room_id,
            "user_id": new_booking.user_id,
            "start_date": new_booking.start_date.isoformat(),
            "end_date": new_booking.end_date.isoformat()
        }
    }), 201
