from datetime import date
from marshmallow import ValidationError
from app.schemas.booking import BookingCreateSchema, BookingResponseSchema

# Step 1: Simulate valid input
valid_input = {
    "room_id": 1,
    "check_in": str(date.today()),
    "check_out": str(date.today().replace(day=date.today().day + 2)),
    "guests": 2
}

# Step 2: Try loading valid input
try:
    schema = BookingCreateSchema()
    result = schema.load(valid_input)
    print("VALID INPUT PARSED:", result)
except ValidationError as err:
    print("VALIDATION ERRORS (valid input):", err.messages)

# Step 3: Simulate bad input
invalid_input = {
    "room_id": "abc",  # should be int
    "check_in": "not-a-date",
    "check_out": "2025-01-01",  # valid date but in the past
    "guests": 0  # invalid
}

try:
    schema = BookingCreateSchema()
    result = schema.load(invalid_input)
    print("INVALID INPUT PARSED:", result)
except ValidationError as err:
    print("VALIDATION ERRORS (invalid input):", err.messages)
