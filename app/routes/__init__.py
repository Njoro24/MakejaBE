from flask import Blueprint
from .booking import booking_bp  # Make sure this matches what's inside booking.py

def register_routes(app):
    app.register_blueprint(booking_bp)
