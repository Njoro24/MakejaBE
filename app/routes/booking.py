from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from marshmallow import ValidationError

from app.schemas.booking_schema import BookingCreateSchema, BookingResponseSchema
from app.services.booking_service import create_booking
from app.models.booking import Booking
from app.models.user import User
from app.utils.exceptions import RoomNotFound, BookingConflict, InvalidBookingDates
from app.extensions import db

booking_bp = Blueprint('booking', __name__)
create_schema = BookingCreateSchema()
response_schema = BookingResponseSchema()

@booking_bp.route('/bookings', methods=['POST'])
@jwt_required()
def book():
    user_id = get_jwt_identity()
    try:
        data = create_schema.load(request.json)
        booking = create_booking(user_id, data)
        return response_schema.dump(booking), 201

    except ValidationError as err:
        return {'errors': err.messages}, 400
    except RoomNotFound as err:
        return {'error': str(err)}, 404
    except InvalidBookingDates as err:
        return {'error': str(err)}, 400
    except BookingConflict as err:
        return {'error': str(err)}, 409
    except Exception:
        return {'error': 'Internal server error'}, 500

@booking_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    if user.role == 'admin':
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    else:
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()

    return response_schema.dump(bookings, many=True), 200

@booking_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking_by_id(booking_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    booking = Booking.query.get_or_404(booking_id)

    if user.role != 'admin' and booking.user_id != user_id:
        return {'error': 'Access denied'}, 403

    return response_schema.dump(booking), 200

@booking_bp.route('/test-login', methods=['POST'])
def test_login():
    # For development only – remove in production
    test_user_id = 1
    token = create_access_token(identity=test_user_id)
    return jsonify(access_token=token)
