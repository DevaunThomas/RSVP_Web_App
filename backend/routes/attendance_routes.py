from flask import Blueprint, jsonify, request
import sqlite3

from models.attendance import Attendance
from models.event import Event
from models.rsvp import RSVP
from models.user import User

attendance_routes = Blueprint("attendance_routes", __name__)


@attendance_routes.post("/events/<int:event_id>/check-in")
def check_in(event_id: int):
    """Marks a user as checked-in (attended) for an event."""
    event = Event.get_by_id(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    if event["status"] == "Canceled":
        return jsonify({"error": "Cannot check in to a canceled event"}), 400

    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Verify if user has a registered RSVP
    rsvp = RSVP.get_by_user_and_event(user_id, event_id)
    if not rsvp or rsvp["rsvp_status"] != "Registered":
        return jsonify({
            "error": "User must have a 'Registered' RSVP to check in"
        }), 400

    try:
        Attendance.check_in(user_id, event_id)
        return jsonify({"message": "Check-in successful"}), 200
    except Exception as e:
        return jsonify({
            "error": "Unable to check in",
            "details": str(e)
        }), 500


@attendance_routes.get("/events/<int:event_id>/attendance")
def get_event_attendance(event_id: int):
    """Fetches all check-in/attendance records for an event."""
    event = Event.get_by_id(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    attendance_list = Attendance.get_for_event(event_id)
    return jsonify(attendance_list), 200


@attendance_routes.get("/users/<int:user_id>/attendance")
def get_user_attendance(user_id: int):
    """Fetches all events a user has attended or checked in for."""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    attendance_list = Attendance.get_for_user(user_id)
    return jsonify(attendance_list), 200


@attendance_routes.patch("/events/<int:event_id>/attendance/<int:user_id>")
def update_attendance_status(event_id: int, user_id: int):
    """Manually updates (toggles) attendance state for a user at an event."""
    event = Event.get_by_id(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    attended = data.get("attended")

    if attended is None:
        return jsonify({"error": "attended boolean field is required"}), 400

    # Ensure attended is a boolean
    if not isinstance(attended, bool):
        return jsonify({"error": "attended field must be a boolean"}), 400

    # If setting to true, check if user has a registered RSVP
    if attended:
        rsvp = RSVP.get_by_user_and_event(user_id, event_id)
        if not rsvp or rsvp["rsvp_status"] != "Registered":
            return jsonify({
                "error": "User must have a 'Registered' RSVP to mark as attended"
            }), 400

    try:
        Attendance.update_attendance(user_id, event_id, attended)
        return jsonify({"message": "Attendance status updated successfully"}), 200
    except Exception as e:
        return jsonify({
            "error": "Unable to update attendance status",
            "details": str(e)
        }), 500


@attendance_routes.delete("/events/<int:event_id>/attendance/<int:user_id>")
def delete_attendance(event_id: int, user_id: int):
    """Deletes an attendance record."""
    event = Event.get_by_id(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    record = Attendance.get_by_user_and_event(user_id, event_id)
    if not record:
        return jsonify({"error": "Attendance record not found"}), 404

    try:
        Attendance.delete(user_id, event_id)
        return jsonify({"message": "Attendance record deleted successfully"}), 200
    except Exception as e:
        return jsonify({
            "error": "Unable to delete attendance record",
            "details": str(e)
        }), 500
