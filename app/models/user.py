from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='user')  
    is_admin = db.Column(db.Boolean, default=False)

    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    rooms = db.relationship('Room', back_populates='host', lazy=True)
    bookings = db.relationship('Booking', back_populates='user', lazy=True)

    reset_token = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
