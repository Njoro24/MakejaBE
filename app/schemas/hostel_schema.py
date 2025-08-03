from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class HostelCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    location = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True)
    description = fields.Str(missing="")
    amenities = fields.List(fields.Str(), missing=[])
    available = fields.Bool(missing=True)


class HostelUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1))
    location = fields.Str(validate=validate.Length(min=1))
    price = fields.Float()
    description = fields.Str()
    amenities = fields.List(fields.Str())
    available = fields.Bool()


class HostelResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    location = fields.Str()
    price = fields.Float()
    description = fields.Str()
    amenities = fields.List(fields.Str())
    available = fields.Bool()
    owner_id = fields.Int()
