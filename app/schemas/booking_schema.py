from marshmallow import Schema, fields, validate

class BookingCreateSchema(Schema):
    room_id = fields.Int(required=True)
    check_in = fields.Date(required=True)
    check_out = fields.Date(required=True)
    guests = fields.Int(required=True, validate=validate.Range(min=1))

class BookingResponseSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    room_id = fields.Int()
    check_in = fields.Date()
    check_out = fields.Date()
    guests = fields.Int()
    total_price = fields.Float()
    status = fields.Str()
    created_at = fields.DateTime()

# Schema instances
booking_schema = BookingCreateSchema()
booking_response_schema = BookingResponseSchema()
