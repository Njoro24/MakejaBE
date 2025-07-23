from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from marshmallow import ValidationError
from app.schemas.booking_schema import BookingCreateSchema, BookingResponseSchema
from app.services.booking_service import create_booking

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
    except Exception as e:
        return {'error': str(e)}, 500

# Add this below your existing code:
@booking_bp.route('/test-login', methods=['POST'])
def test_login():
    # In real use, you'd verify credentials here
    test_user_id = 1  # fake user
    token = create_access_token(identity=test_user_id)
    return jsonify(access_token=token)
