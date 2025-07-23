from app.extensions import db
from app.models.room import Room
from app.models.booking import Booking
from datetime import datetime

def calculate_price(check_in, check_out, room_price):
    days = (check_out - check_in).days
    return max(days, 1) * room_price

def create_booking(user_id, data):
    # Validate room existence
    room = Room.query.get(data['room_id'])
    if not room:
        raise ValueError("Room not found")

    # Validate check-in and check-out dates
    if data['check_out'] <= data['check_in']:
        raise ValueError("Check-out date must be after check-in date")

    # Check for booking conflicts
    conflicting = Booking.query.filter(
        Booking.room_id == data['room_id'],
        Booking.check_out > data['check_in'],
        Booking.check_in < data['check_out']
    ).first()
    if conflicting:
        raise ValueError("Room is not available for the selected dates")

    # Calculate total price
    total_price = calculate_price(data['check_in'], data['check_out'], room.price)

    # Create and store booking
    booking = Booking(
        user_id=user_id,
        room_id=data['room_id'],
        check_in=data['check_in'],
        check_out=data['check_out'],
        guests=data['guests'],
        total_price=total_price,
        status='pending'
    )

    db.session.add(booking)
    db.session.commit()
    return booking
