from app.db import db
from datetime import datetime

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")  # optional with default
    price_per_night = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), default="standard")  # optional with default
    image = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    host = db.relationship('User', back_populates='rooms')

    bookings = db.relationship('Booking', back_populates='room', lazy=True)
