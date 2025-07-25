# app/schemas/payment_schema.py

from marshmallow import Schema, fields, validate

class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True)
    method = fields.Str(required=True, validate=validate.OneOf(["mpesa", "card", "bank"]))
    transaction_id = fields.Str()
    status = fields.Str(dump_only=True)
    booking_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
