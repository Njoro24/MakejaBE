# app/models/hostel.py

from datetime import datetime
from app.extensions import db

class Hostel(db.Model):
    __tablename__ = 'hostels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)

    # Use TEXT instead of ARRAY for broader DB support like SQLite
    amenities = db.Column(db.Text)  # Store comma-separated amenities if needed

    image_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rooms = db.relationship("Room", backref="hostel", cascade="all, delete", lazy=True)

    def __repr__(self):
        return f"<Hostel {self.name}>"
