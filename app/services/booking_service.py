from datetime import datetime
from app.extensions import db
from app.models.room import Room
from app.models.booking import Booking
from app.utils.exceptions import (
    BookingConflict,
    RoomNotFound,
    InvalidBookingDates,
    TooManyGuests
)

def calculate_price(check_in, check_out, price_per_night):
    days = (check_out - check_in).days
    return max(days, 1) * price_per_night

def is_date_in_past(date):
    return date < datetime.utcnow().date()

def validate_booking_dates(check_in, check_out):
    if check_in >= check_out:
        raise InvalidBookingDates("Check-out must be after check-in.")
    if is_date_in_past(check_in):
        raise InvalidBookingDates("Cannot book for past dates.")

def check_room_availability(room_id, check_in, check_out):
    conflict = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.check_out > check_in,
        Booking.check_in < check_out
    ).first()
    if conflict:
        raise BookingConflict("Room is already booked for the selected dates.")

def create_booking(user_id, data):
    room = Room.query.get(data['room_id'])
    if not room:
        raise RoomNotFound("Room not found.")

    check_in = data['check_in']
    check_out = data['check_out']
    guests = data['guests']

    validate_booking_dates(check_in, check_out)
    check_room_availability(room.id, check_in, check_out)

    if guests > room.capacity:
        raise TooManyGuests("Number of guests exceeds room capacity.")

    total_price = calculate_price(check_in, check_out, room.price)

    booking = Booking(
        guest_id=user_id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        total_price=total_price,
        status='pending'
    )

    db.session.add(booking)
    db.session.commit()
    return booking
