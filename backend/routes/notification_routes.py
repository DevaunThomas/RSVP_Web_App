from flask import Blueprint, g, jsonify, request
from models.notification import Notification
from models.user import User
from services.auth_service import token_required

notification_routes = Blueprint("notification_routes", __name__)


@notification_routes.get("/users/<int:user_id>/notifications")
@token_required
def get_user_notifications(user_id: int):
    """Retrieves all notifications for a user."""
    if not User.get_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    if g.current_user["user_id"] != user_id and g.current_user.get("role") != "organizer":
        return jsonify({"error": "Unauthorized to view these notifications"}), 403

    notifications = Notification.get_for_user(user_id)
    return jsonify(notifications), 200


@notification_routes.get("/users/<int:user_id>/notifications/unread-count")
@token_required
def get_unread_notification_count(user_id: int):
    """Retrieves the count of unread notifications for a user."""
    if not User.get_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    if g.current_user["user_id"] != user_id and g.current_user.get("role") != "organizer":
        return jsonify({"error": "Unauthorized to view notification count"}), 403

    count = Notification.get_unread_count(user_id)
    return jsonify({"unread_count": count}), 200


@notification_routes.patch("/notifications/<int:notification_id>/read")
@token_required
def mark_notification_read(notification_id: int):
    """Marks a single notification as read."""
    notification = Notification.get_by_id(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    if notification["user_id"] != g.current_user["user_id"] and g.current_user.get("role") != "organizer":
        return jsonify({"error": "Unauthorized to modify this notification"}), 403

    Notification.mark_as_read(notification_id)
    return jsonify({"message": "Notification marked as read"}), 200


@notification_routes.patch("/users/<int:user_id>/notifications/read-all")
@token_required
def mark_all_notifications_read(user_id: int):
    """Marks all notifications for a user as read."""
    if not User.get_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    if g.current_user["user_id"] != user_id and g.current_user.get("role") != "organizer":
        return jsonify({"error": "Unauthorized to modify these notifications"}), 403

    Notification.mark_all_as_read(user_id)
    return jsonify({"message": "All notifications marked as read"}), 200


@notification_routes.delete("/notifications/<int:notification_id>")
@token_required
def delete_notification(notification_id: int):
    """Deletes a notification."""
    notification = Notification.get_by_id(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    if notification["user_id"] != g.current_user["user_id"] and g.current_user.get("role") != "organizer":
        return jsonify({"error": "Unauthorized to delete this notification"}), 403

    Notification.delete(notification_id)
    return jsonify({"message": "Notification deleted successfully"}), 200
