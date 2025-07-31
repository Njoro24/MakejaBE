from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from app.models.booking import Booking
from app.schemas.user_schema import UserResponseSchema as UserSchema
from app.schemas.room_schema import RoomSchema

class BookingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        load_instance = True
        include_fk = True
        exclude = ('updated_at',)

    user = fields.Nested(UserSchema, dump_only=True)
    room = fields.Nested(RoomSchema, dump_only=True)
