import sqlite3

from flask import Blueprint, jsonify, request

from models.event import Event
from models.user import User


event_routes = Blueprint("event_routes", __name__)


@event_routes.post("/events")
def create_event():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "title",
        "event_date",
        "event_time",
        "location",
        "capacity",
        "organizer_id"
    ]

    missing_fields = [
        field for field in required_fields
        if data.get(field) in (None, "")
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    organizer = User.get_by_id(data["organizer_id"])

    if not organizer:
        return jsonify({"error": "Organizer not found"}), 404

    if organizer["role"] != "organizer":
        return jsonify({
            "error": "The selected user is not an organizer"
        }), 403

    try:
        capacity = int(data["capacity"])

        if capacity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({
            "error": "Capacity must be a positive integer"
        }), 400

    try:
        event_id = Event.create(
            title=data["title"].strip(),
            description=data.get("description", "").strip(),
            event_date=data["event_date"],
            event_time=data["event_time"],
            location=data["location"].strip(),
            capacity=capacity,
            organizer_id=data["organizer_id"]
        )

        return jsonify({
            "message": "Event created successfully",
            "event_id": event_id
        }), 201

    except sqlite3.IntegrityError as error:
        return jsonify({
            "error": "Unable to create event",
            "details": str(error)
        }), 400


@event_routes.get("/events")
def get_events():
    include_canceled = (
        request.args.get("include_canceled", "false").lower() == "true"
    )

    if include_canceled:
        events = Event.get_all()
    else:
        events = Event.get_active()

    return jsonify(events), 200


@event_routes.get("/events/<int:event_id>")
def get_event(event_id: int):
    event = Event.get_by_id(event_id)

    if not event:
        return jsonify({"error": "Event not found"}), 404

    event["registered_count"] = Event.get_registered_count(event_id)

    return jsonify(event), 200


@event_routes.get("/organizers/<int:organizer_id>/events")
def get_organizer_events(organizer_id: int):
    organizer = User.get_by_id(organizer_id)

    if not organizer:
        return jsonify({"error": "Organizer not found"}), 404

    return jsonify(Event.get_by_organizer(organizer_id)), 200


@event_routes.put("/events/<int:event_id>")
def update_event(event_id: int):
    existing_event = Event.get_by_id(event_id)

    if not existing_event:
        return jsonify({"error": "Event not found"}), 404

    data = request.get_json(silent=True) or {}

    required_fields = [
        "title",
        "event_date",
        "event_time",
        "location",
        "capacity"
    ]

    missing_fields = [
        field for field in required_fields
        if data.get(field) in (None, "")
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    try:
        capacity = int(data["capacity"])

        if capacity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({
            "error": "Capacity must be a positive integer"
        }), 400

    status = data.get("status", "Updated")

    if status not in ("Active", "Updated", "Canceled"):
        return jsonify({
            "error": "Invalid event status"
        }), 400

    Event.update(
        event_id=event_id,
        title=data["title"].strip(),
        description=data.get("description", "").strip(),
        event_date=data["event_date"],
        event_time=data["event_time"],
        location=data["location"].strip(),
        capacity=capacity,
        status=status
    )

    return jsonify({
        "message": "Event updated successfully"
    }), 200


@event_routes.patch("/events/<int:event_id>/cancel")
def cancel_event(event_id: int):
    if not Event.get_by_id(event_id):
        return jsonify({"error": "Event not found"}), 404

    Event.cancel(event_id)

    return jsonify({
        "message": "Event canceled successfully"
    }), 200


@event_routes.delete("/events/<int:event_id>")
def delete_event(event_id: int):
    if not Event.get_by_id(event_id):
        return jsonify({"error": "Event not found"}), 404

    Event.delete(event_id)

    return jsonify({
        "message": "Event deleted successfully"
    }), 200