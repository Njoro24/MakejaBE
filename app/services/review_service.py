from app.db import db
from app.models.review import Review

class ReviewService:
    @staticmethod
    def create_review(user_id, hostel_id, rating, comment):
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5 stars")

        review = Review(
            user_id=user_id,
            hostel_id=hostel_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        return review

    @staticmethod
    def flag_review(review_id):
        review = Review.query.get_or_404(review_id)
        review.is_flagged = True
        db.session.commit()
        return review

    @staticmethod
    def get_reviews_by_hostel(hostel_id):
        reviews = Review.query.filter_by(hostel_id=hostel_id).all()
        return reviews
