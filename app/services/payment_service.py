# app/services/payment_service.py

from app.models.payment import Payment
from app.extensions import db


def create_payment(payment_data):
    new_payment = Payment(**payment_data)
    db.session.add(new_payment)
    db.session.commit()
    return new_payment


def get_all_payments():
    return Payment.query.all()


def get_payment_by_id(payment_id):
    return Payment.query.get(payment_id)
