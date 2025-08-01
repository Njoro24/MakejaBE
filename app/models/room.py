from app.db import db

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price_per_night = db.Column(db.Float, nullable=False)

    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    host = db.relationship('User')

    bookings = db.relationship('Booking', back_populates='room', lazy=True)
