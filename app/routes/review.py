from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.review import Review
from app.schemas.review_schema import ReviewSchema
from app.services.review_service import ReviewService

review_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')
review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)

@review_bp.route('/', methods=['POST'])
@jwt_required()
def create_review():
    """Create a new review"""
    data = request.get_json()
    errors = review_schema.validate(data)
    if errors:
        return jsonify({"error": errors}), 400

    user_id = get_jwt_identity()

    try:
        hostel_id = data['hostel_id']
        rating = data['rating']
        comment = data.get('comment', '')

        # Call ReviewService with explicit arguments
        review = ReviewService.create_review(
            user_id=user_id,
            hostel_id=hostel_id,
            rating=rating,
            comment=comment
        )

        return jsonify(review_schema.dump(review)), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@review_bp.route('/hostel/<int:hostel_id>', methods=['GET'])
def get_hostel_reviews(hostel_id):
    """Get reviews for a specific hostel"""
    reviews = Review.query.filter_by(hostel_id=hostel_id).all()
    return jsonify(reviews_schema.dump(reviews)), 200

@review_bp.route('/', methods=['GET'])
def get_all_reviews():
    """Get all reviews"""
    reviews = Review.query.all()
    return jsonify(reviews_schema.dump(reviews)), 200

@review_bp.route('/test', methods=['GET'])
def test_route():
    """Test route to confirm reviews endpoint"""
    return jsonify({"message": "Review route working!"}), 200
