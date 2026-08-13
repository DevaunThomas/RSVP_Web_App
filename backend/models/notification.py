from typing import Any, Dict, List, Optional
from database import DatabaseHelper


class Notification:
    """Database operations for notifications."""

    @staticmethod
    def create(
        user_id: int,
        event_id: int,
        message: str,
        notification_type: str
    ) -> int:
        query = """
            INSERT INTO Notifications (user_id, event_id, message, notification_type)
            VALUES (?, ?, ?, ?)
        """
        return DatabaseHelper.execute_write(
            query,
            (user_id, event_id, message, notification_type)
        )

    @staticmethod
    def get_by_id(notification_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT notification_id, user_id, event_id, message, notification_type, sent_at, read_status
            FROM Notifications
            WHERE notification_id = ?
        """
        return DatabaseHelper.execute_query_one(query, (notification_id,))

    @staticmethod
    def get_for_user(user_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT n.notification_id, n.user_id, n.event_id, n.message,
                   n.notification_type, n.sent_at, n.read_status,
                   e.title AS event_title
            FROM Notifications n
            JOIN Events e ON n.event_id = e.event_id
            WHERE n.user_id = ?
            ORDER BY n.sent_at DESC
        """
        return DatabaseHelper.execute_query(query, (user_id,))

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        query = """
            SELECT COUNT(*) as unread_count
            FROM Notifications
            WHERE user_id = ? AND read_status = 0
        """
        result = DatabaseHelper.execute_query_one(query, (user_id,))
        return result["unread_count"] if result else 0

    @staticmethod
    def mark_as_read(notification_id: int) -> int:
        query = """
            UPDATE Notifications
            SET read_status = 1
            WHERE notification_id = ?
        """
        return DatabaseHelper.execute_write(query, (notification_id,))

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        query = """
            UPDATE Notifications
            SET read_status = 1
            WHERE user_id = ?
        """
        return DatabaseHelper.execute_write(query, (user_id,))

    @staticmethod
    def delete(notification_id: int) -> int:
        query = "DELETE FROM Notifications WHERE notification_id = ?"
        return DatabaseHelper.execute_write(query, (notification_id,))
