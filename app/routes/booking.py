from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.booking import Booking
from app.schemas.booking_schema import BookingSchema
from app.db import db
from marshmallow import ValidationError
from datetime import datetime

booking_bp = Blueprint('booking_bp', __name__)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# GET /bookings - return current user's bookings
@booking_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    current_user = get_jwt_identity()
    user_bookings = Booking.query.filter_by(user_id=current_user['id']).all()
    return bookings_schema.jsonify(user_bookings), 200

# POST /bookings - create a new booking
@booking_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json()
    current_user = get_jwt_identity()

    try:
        validated = booking_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    room_id = validated['room_id']
    check_in = validated['check_in']
    check_out = validated['check_out']
    total_price = validated['total_price']

    # Check for booking conflicts
    overlap = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status == 'approved',
        Booking.check_in < check_out,
        Booking.check_out > check_in
    ).first()

    if overlap:
        return jsonify({'error': 'Room is already booked for the selected dates'}), 409

    new_booking = Booking(
        user_id=current_user['id'],
        room_id=room_id,
        check_in=check_in,
        check_out=check_out,
        total_price=total_price,
        status='pending'  
    )

    db.session.add(new_booking)
    db.session.commit()

    return booking_schema.jsonify(new_booking), 201
