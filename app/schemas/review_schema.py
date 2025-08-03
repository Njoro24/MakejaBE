from marshmallow import Schema, fields, validate

class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    hostel_id = fields.Int(required=True)
    rating = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=5, error="Rating must be 1-5 stars")
    )
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    is_flagged = fields.Bool(dump_only=True)
