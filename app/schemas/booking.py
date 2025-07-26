from marshmallow import Schema, fields, validates, ValidationError
from datetime import date

class BookingCreateSchema(Schema):
    room_id = fields.Integer(required=True)
    check_in = fields.Date(required=True)
    check_out = fields.Date(required=True)
    guests = fields.Integer(required=True)

    @validates("check_in")
    def validate_check_in(self, value):
        if value < date.today():
            raise ValidationError("Check-in date cannot be in the past.")

    @validates("check_out")
    def validate_check_out(self, value):
        if value < date.today():
            raise ValidationError("Check-out date cannot be in the past.")

    @validates("guests")
    def validate_guests(self, value):
        if value <= 0:
            raise ValidationError("Number of guests must be at least 1.")

class BookingResponseSchema(Schema):
    id = fields.Integer()
    room_id = fields.Integer()
    check_in = fields.Date()
    check_out = fields.Date()
    guests = fields.Integer()
    total_price = fields.Float()
    user_id = fields.Integer()
