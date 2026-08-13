import sqlite3

from flask import Blueprint, g, jsonify, request

from models.event import Event
from models.user import User
from services.auth_service import organizer_required, token_required
from services.notification_service import NotificationService


event_routes = Blueprint("event_routes", __name__)


@event_routes.post("/events")
@organizer_required
def create_event():
    data = request.get_json(silent=True) or {}

    # Default organizer_id from authenticated user if not provided
    organizer_id = data.get("organizer_id", g.current_user["user_id"])

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

    organizer = User.get_by_id(organizer_id)

    if not organizer:
        return jsonify({"error": "Organizer not found"}), 404

    if organizer["role"] != "organizer":
        return jsonify({
            "error": "The selected user is not an organizer"
        }), 403

    if g.current_user["user_id"] != organizer_id:
        return jsonify({
            "error": "Unauthorized to create an event for another organizer"
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
            organizer_id=organizer_id
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
@token_required
def get_organizer_events(organizer_id: int):
    organizer = User.get_by_id(organizer_id)

    if not organizer:
        return jsonify({"error": "Organizer not found"}), 404

    return jsonify(Event.get_by_organizer(organizer_id)), 200


@event_routes.put("/events/<int:event_id>")
@organizer_required
def update_event(event_id: int):
    existing_event = Event.get_by_id(event_id)

    if not existing_event:
        return jsonify({"error": "Event not found"}), 404

    if existing_event["organizer_id"] != g.current_user["user_id"]:
        return jsonify({"error": "Unauthorized to modify this event"}), 403

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

    # Automatically notify attendees of the event update
    NotificationService.notify_event_update(event_id, data["title"].strip())

    return jsonify({
        "message": "Event updated successfully"
    }), 200


@event_routes.patch("/events/<int:event_id>/cancel")
@organizer_required
def cancel_event(event_id: int):
    existing_event = Event.get_by_id(event_id)

    if not existing_event:
        return jsonify({"error": "Event not found"}), 404

    if existing_event["organizer_id"] != g.current_user["user_id"]:
        return jsonify({"error": "Unauthorized to cancel this event"}), 403

    Event.cancel(event_id)

    # Automatically notify attendees of event cancellation
    NotificationService.notify_event_cancellation(event_id, existing_event["title"])

    return jsonify({
        "message": "Event canceled successfully"
    }), 200


@event_routes.delete("/events/<int:event_id>")
@organizer_required
def delete_event(event_id: int):
    existing_event = Event.get_by_id(event_id)

    if not existing_event:
        return jsonify({"error": "Event not found"}), 404

    if existing_event["organizer_id"] != g.current_user["user_id"]:
        return jsonify({"error": "Unauthorized to delete this event"}), 403

    Event.delete(event_id)

    return jsonify({
        "message": "Event deleted successfully"
    }), 200