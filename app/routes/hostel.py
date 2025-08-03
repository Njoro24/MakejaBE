from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.hostel_schema import (
    HostelCreateSchema,
    HostelUpdateSchema,
    HostelResponseSchema
)
from app.services.hostel_service import (
    create_hostel,
    get_all_hostels,
    get_hostel_by_id,
    update_hostel,
    delete_hostel
)
from app.models import User
from app.extensions import db

hostel_bp = Blueprint("hostel_bp", __name__, url_prefix="/api/hostels")


@hostel_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    user_id = get_jwt_identity()
    data = request.get_json()

    schema = HostelCreateSchema()
    try:
        hostel_data = schema.load(data)
    except Exception as err:
        return jsonify({"error": str(err)}), 400

    new_hostel = create_hostel(hostel_data, owner_id=user_id)
    response = HostelResponseSchema().dump(new_hostel)
    return jsonify(response), 201


@hostel_bp.route("/", methods=["GET"])
def list_hostels():
    hostels = get_all_hostels()
    response = HostelResponseSchema(many=True).dump(hostels)
    return jsonify(response), 200


@hostel_bp.route("/<int:hostel_id>", methods=["GET"])
def retrieve(hostel_id):
    hostel = get_hostel_by_id(hostel_id)
    if not hostel:
        return jsonify({"error": "Hostel not found"}), 404

    response = HostelResponseSchema().dump(hostel)
    return jsonify(response), 200


@hostel_bp.route("/<int:hostel_id>", methods=["PATCH"])
@jwt_required()
def update(hostel_id):
    user_id = get_jwt_identity()
    hostel = get_hostel_by_id(hostel_id)
    if not hostel:
        return jsonify({"error": "Hostel not found"}), 404

    user = User.query.get(user_id)
    if hostel.owner_id != user_id and user.role != "admin":
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json()
    try:
        validated_data = HostelUpdateSchema().load(data)
    except Exception as err:
        return jsonify({"error": str(err)}), 400

    updated_hostel = update_hostel(hostel_id, validated_data)
    response = HostelResponseSchema().dump(updated_hostel)
    return jsonify(response), 200


@hostel_bp.route("/<int:hostel_id>", methods=["DELETE"])
@jwt_required()
def delete(hostel_id):
    user_id = get_jwt_identity()
    hostel = get_hostel_by_id(hostel_id)
    if not hostel:
        return jsonify({"error": "Hostel not found"}), 404

    user = User.query.get(user_id)
    if hostel.owner_id != user_id and user.role != "admin":
        return jsonify({"error": "Not authorized"}), 403

    delete_hostel(hostel_id)
    return jsonify({"message": "Hostel deleted"}), 200
