# app/schemas/hostel_schema.py

from marshmallow import Schema, fields, validate, validates, ValidationError

class HostelCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    description = fields.String(required=True, validate=validate.Length(min=10))
    location = fields.String(required=True)
    price_per_night = fields.Float(required=True)
    amenities = fields.List(fields.String(), required=False)
    host_id = fields.Integer(required=True)

    @validates("price_per_night")
    def validate_price(self, value):
        if value <= 0:
            raise ValidationError("Price per night must be greater than zero.")

class HostelUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=2, max=100))
    description = fields.String(validate=validate.Length(min=10))
    location = fields.String()
    price_per_night = fields.Float()
    amenities = fields.List(fields.String())

    @validates("price_per_night")
    def validate_price(self, value):
        if value is not None and value <= 0:
            raise ValidationError("Price per night must be greater than zero.")

class HostelResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    location = fields.String()
    price_per_night = fields.Float()
    amenities = fields.List(fields.String())
    host_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
