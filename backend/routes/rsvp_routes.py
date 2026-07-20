import sqlite3

from flask import Blueprint, jsonify, request

from models.event import Event
from models.rsvp import RSVP
from models.user import User


rsvp_routes = Blueprint("rsvp_routes", __name__)


@rsvp_routes.post("/rsvps")
def create_rsvp():
    data = request.get_json(silent=True) or {}

    if data.get("user_id") is None or data.get("event_id") is None:
        return jsonify({
            "error": "user_id and event_id are required"
        }), 400

    user_id = data["user_id"]
    event_id = data["event_id"]

    user = User.get_by_id(user_id)
    event = Event.get_by_id(event_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not event:
        return jsonify({"error": "Event not found"}), 404

    if event["status"] == "Canceled":
        return jsonify({
            "error": "Cannot RSVP to a canceled event"
        }), 400

    existing_rsvp = RSVP.get_by_user_and_event(user_id, event_id)

    if existing_rsvp:
        if existing_rsvp["rsvp_status"] == "Canceled":
            registered_count = Event.get_registered_count(event_id)

            new_status = (
                "Registered"
                if registered_count < event["capacity"]
                else "Waitlisted"
            )

            RSVP.update_status(
                existing_rsvp["rsvp_id"],
                new_status
            )

            return jsonify({
                "message": "RSVP restored successfully",
                "rsvp_id": existing_rsvp["rsvp_id"],
                "rsvp_status": new_status
            }), 200

        return jsonify({
            "error": "User has already responded to this event",
            "rsvp_status": existing_rsvp["rsvp_status"]
        }), 409

    registered_count = Event.get_registered_count(event_id)

    rsvp_status = (
        "Registered"
        if registered_count < event["capacity"]
        else "Waitlisted"
    )

    try:
        rsvp_id = RSVP.create(
            user_id=user_id,
            event_id=event_id,
            rsvp_status=rsvp_status
        )

        return jsonify({
            "message": "RSVP created successfully",
            "rsvp_id": rsvp_id,
            "rsvp_status": rsvp_status
        }), 201

    except sqlite3.IntegrityError as error:
        return jsonify({
            "error": "Unable to create RSVP",
            "details": str(error)
        }), 400


@rsvp_routes.get("/rsvps/<int:rsvp_id>")
def get_rsvp(rsvp_id: int):
    rsvp = RSVP.get_by_id(rsvp_id)

    if not rsvp:
        return jsonify({"error": "RSVP not found"}), 404

    return jsonify(rsvp), 200


@rsvp_routes.get("/users/<int:user_id>/rsvps")
def get_user_rsvps(user_id: int):
    if not User.get_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    return jsonify(RSVP.get_for_user(user_id)), 200


@rsvp_routes.get("/events/<int:event_id>/rsvps")
def get_event_rsvps(event_id: int):
    if not Event.get_by_id(event_id):
        return jsonify({"error": "Event not found"}), 404

    return jsonify(RSVP.get_for_event(event_id)), 200


@rsvp_routes.patch("/rsvps/<int:rsvp_id>")
def update_rsvp(rsvp_id: int):
    rsvp = RSVP.get_by_id(rsvp_id)

    if not rsvp:
        return jsonify({"error": "RSVP not found"}), 404

    data = request.get_json(silent=True) or {}
    rsvp_status = data.get("rsvp_status")

    if rsvp_status not in ("Registered", "Canceled", "Waitlisted"):
        return jsonify({
            "error": "Invalid RSVP status"
        }), 400

    RSVP.update_status(rsvp_id, rsvp_status)

    return jsonify({
        "message": "RSVP updated successfully",
        "rsvp_status": rsvp_status
    }), 200


@rsvp_routes.patch("/rsvps/<int:rsvp_id>/cancel")
def cancel_rsvp(rsvp_id: int):
    if not RSVP.get_by_id(rsvp_id):
        return jsonify({"error": "RSVP not found"}), 404

    RSVP.update_status(rsvp_id, "Canceled")

    return jsonify({
        "message": "RSVP canceled successfully"
    }), 200


@rsvp_routes.delete("/rsvps/<int:rsvp_id>")
def delete_rsvp(rsvp_id: int):
    if not RSVP.get_by_id(rsvp_id):
        return jsonify({"error": "RSVP not found"}), 404

    RSVP.delete(rsvp_id)

    return jsonify({
        "message": "RSVP deleted successfully"
    }), 200