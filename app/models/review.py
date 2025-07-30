from datetime import datetime
from app.db import db

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hostel_id = db.Column(db.Integer, nullable=True)  # FK removed temporarily
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_flagged = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="reviews", lazy="joined")
    # hostel = db.relationship("Hostel", backref="reviews", lazy="joined")

    def __repr__(self):
        return f'<Review {self.id}>'
