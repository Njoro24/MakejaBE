# app/routes/payment.py

from flask import Blueprint, request, jsonify
from app.services.payment_service import (
    create_payment,
    get_all_payments,
    get_payment_by_id,
)
from app.schemas.payment_schema import PaymentSchema
from marshmallow import ValidationError

payment_bp = Blueprint("payment", __name__)
payment_schema = PaymentSchema()
payment_list_schema = PaymentSchema(many=True)


@payment_bp.route("/payments", methods=["POST"])
def handle_create_payment():
    try:
        payment_data = payment_schema.load(request.json)
        new_payment = create_payment(payment_data)
        return payment_schema.jsonify(new_payment), 201
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_bp.route("/payments", methods=["GET"])
def handle_get_all_payments():
    try:
        payments = get_all_payments()
        return payment_list_schema.jsonify(payments), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_bp.route("/payments/<int:payment_id>", methods=["GET"])
def handle_get_payment(payment_id):
    try:
        payment = get_payment_by_id(payment_id)
        if payment:
            return payment_schema.jsonify(payment), 200
        else:
            return jsonify({"error": "Payment not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
