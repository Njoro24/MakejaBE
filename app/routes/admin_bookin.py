from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.middleware.auth_middleware import admin_required
from app.models import Booking, User, Room
from app.extensions import db

admin_booking_bp = Blueprint('admin_booking_bp', __name__)

@admin_booking_bp.route('/admin/bookings', methods=['GET'])
@jwt_required()
@admin_required
def get_all_bookings():
    bookings = Booking.query.all()
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "user": {
                "id": b.user.id,
                "name": b.user.name,
                "email": b.user.email
            },
            "room": {
                "id": b.room.id,
                "name": b.room.name
            },
            "check_in": b.check_in.isoformat(),
            "check_out": b.check_out.isoformat(),
            "status": b.status,
            "created_at": b.created_at.isoformat()
        })
    return jsonify(result), 200

@admin_booking_bp.route('/admin/bookings/<int:booking_id>/cancel', methods=['PATCH'])
@jwt_required()
@admin_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'cancelled'
    db.session.commit()
    return jsonify({"message": "Booking cancelled by admin"}), 200
