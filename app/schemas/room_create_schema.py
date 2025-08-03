from marshmallow import Schema, fields, validate

class RoomCreateSchema(Schema):
    id = fields.Int(dump_only=True)

    title = fields.Str(required=True)
    location = fields.Str(required=True)
    description = fields.Str(required=False, missing="")  # Optional, default empty
    price_per_night = fields.Float(
        required=True, 
        validate=validate.Range(min=0.01, error="Price must be positive")
    )
    capacity = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Capacity must be ≥1")
    )
    category = fields.Str(required=False, missing="standard")  # Optional, default "standard"
    image = fields.Str(required=True)
    

