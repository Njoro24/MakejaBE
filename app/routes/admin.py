from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.review import Review
from app.schemas.review_schema import ReviewSchema
from app.utils.decorators import admin_required
from app.db import db
  

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
review_schema = ReviewSchema()

@admin_bp.route('/reviews', methods=['GET'])
@jwt_required()
@admin_required
def get_all_reviews():
    reviews = Review.query.all()
    return jsonify(review_schema.dump(reviews, many=True)), 200

@admin_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"}), 200
