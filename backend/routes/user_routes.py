import sqlite3

from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from models.user import User
from services.auth_service import generate_token, token_required


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

        token = generate_token(
            user_id=user_id,
            role=data["role"],
            name=data["name"].strip(),
            email=data["email"].strip().lower()
        )

        return jsonify({
            "message": "User created successfully",
            "user_id": user_id,
            "token": token
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "A user with that email already exists"
        }), 409


@user_routes.post("/login")
def login_user():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.get_by_email(email)

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    token = generate_token(
        user_id=user["user_id"],
        role=user["role"],
        name=user["name"],
        email=user["email"]
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200


@user_routes.post("/logout")
def logout_user():
    return jsonify({"message": "Logout successful"}), 200


@user_routes.get("/me")
@token_required
def get_current_user_profile():
    user = User.get_by_id(g.current_user["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@user_routes.get("/users")
@token_required
def get_users():
    return jsonify(User.get_all()), 200


@user_routes.get("/users/<int:user_id>")
@token_required
def get_user(user_id: int):
    user = User.get_by_id(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200


@user_routes.put("/users/<int:user_id>")
@token_required
def update_user(user_id: int):
    if not User.get_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    if g.current_user["user_id"] != user_id and g.current_user.get("role") != "organizer":
        return jsonify({"error": "Unauthorized to update this user"}), 403

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
@token_required
def delete_user(user_id: int):
    if not User.get_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    if g.current_user["user_id"] != user_id and g.current_user.get("role") != "organizer":
        return jsonify({"error": "Unauthorized to delete this user"}), 403

    User.delete(user_id)

    return jsonify({
        "message": "User deleted successfully"
    }), 200