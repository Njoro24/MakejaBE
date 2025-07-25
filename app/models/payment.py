# app/models/payment.py

from datetime import datetime
from app.extensions import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")  # e.g. pending, completed, failed
    method = db.Column(db.String(50), nullable=False)  # e.g. Mpesa, card, PayPal
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)

    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    booking = db.relationship("Booking", backref=db.backref("payments", lazy=True))

    def __repr__(self):
        return f"<Payment {self.id} - {self.status} - {self.amount}>"
