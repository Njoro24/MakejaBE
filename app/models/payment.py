from app.db import db
from datetime import datetime
import uuid

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='KES')
    payment_method = db.Column(db.String(20), nullable=False)  # 'mpesa', 'card', 'bank'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed', 'cancelled'
    
    # M-Pesa specific fields
    phone_number = db.Column(db.String(15))
    mpesa_checkout_request_id = db.Column(db.String(100))
    mpesa_receipt_number = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Additional fields
    description = db.Column(db.Text)
    reference = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.amount} {self.currency} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'phone_number': self.phone_number,
            'mpesa_checkout_request_id': self.mpesa_checkout_request_id,
            'mpesa_receipt_number': self.mpesa_receipt_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'description': self.description,
            'reference': self.reference
        }