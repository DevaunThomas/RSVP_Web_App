import sqlite3

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from models.user import User


user_routes = Blueprint("user_routes", __name__)


@user_routes.post("/users")
def create_user():
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email", "password", "role"]
    missing_fields = [
        field for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    if data["role"] not in ("student", "organizer"):
        return jsonify({
            "error": "Role must be student or organizer"
        }), 400

    try:
        user_id = User.create(
            name=data["name"].strip(),
            email=data["email"].strip().lower(),
            password_hash=generate_password_hash(
                data["password"],
                method="pbkdf2:sha256"
                ),
            role=data["role"]
        )

        return jsonify({
            "message": "User created successfully",
            "user_id": user_id
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "A user with that email already exists"
        }), 409


@user_routes.get("/users")
def get_users():
    return jsonify(User.get_all()), 200


@user_routes.get("/users/<int:user_id>")
def get_user(user_id: int):
    user = User.get_by_id(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200


@user_routes.put("/users/<int:user_id>")
def update_user(user_id: int):
    if not User.get_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email", "role"]
    missing_fields = [
        field for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    if data["role"] not in ("student", "organizer"):
        return jsonify({
            "error": "Role must be student or organizer"
        }), 400

    try:
        User.update(
            user_id=user_id,
            name=data["name"].strip(),
            email=data["email"].strip().lower(),
            role=data["role"]
        )

        return jsonify({
            "message": "User updated successfully"
        }), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "A user with that email already exists"
        }), 409


@user_routes.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    if not User.get_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    User.delete(user_id)

    return jsonify({
        "message": "User deleted successfully"
    }), 200