from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from app.models.room import Room
from app.schemas.user_schema import UserResponseSchema as UserSchema


class RoomSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Room
        load_instance = True
        include_fk = True
        exclude = ['bookings']  # prevent infinite nesting

    host = fields.Nested(UserSchema)


# ✅ Add these instances at the bottom
room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)
