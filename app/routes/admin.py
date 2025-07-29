from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.review import Review
from app.schemas.review_schema import ReviewSchema
from app.models.booking import Booking
from app.schemas.booking_schema import BookingSchema
from app.models.room import Room
from app.schemas.room_schema import RoomSchema
from app.utils.decorators import admin_required
from app.db import db

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# Review Routes

review_schema = ReviewSchema()

@admin_bp.route('/reviews', methods=['GET'])
@jwt_required()
@admin_required
def get_all_reviews():
    reviews = Review.query.all()
    return jsonify(review_schema.dump(reviews, many=True)), 200

@admin_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"}), 200



# Booking Routes


booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
@admin_required
def get_all_bookings():
    bookings = Booking.query.all()
    return bookings_schema.jsonify(bookings), 200

@admin_bp.route('/bookings/<int:booking_id>/status', methods=['PATCH'])
@jwt_required()
@admin_required
def update_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400

    booking = Booking.query.get_or_404(booking_id)
    booking.status = new_status
    db.session.commit()

    return booking_schema.jsonify(booking), 200



# Room Routes


room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)

@admin_bp.route('/rooms', methods=['GET'])
@jwt_required()
@admin_required
def get_all_rooms():
    rooms = Room.query.all()
    return rooms_schema.jsonify(rooms), 200

@admin_bp.route('/rooms', methods=['POST'])
@jwt_required()
@admin_required
def create_room():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    price_per_night = data.get('price_per_night')
    host_id = data.get('host_id')

    if not title or not price_per_night or not host_id:
        return jsonify({'error': 'Missing required fields'}), 400

    new_room = Room(
        title=title,
        description=description,
        price_per_night=price_per_night,
        host_id=host_id
    )

    db.session.add(new_room)
    db.session.commit()
    return room_schema.jsonify(new_room), 201

@admin_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return jsonify({'message': 'Room deleted'}), 200
