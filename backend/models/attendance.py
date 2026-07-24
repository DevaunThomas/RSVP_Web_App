from typing import Any, Dict, List, Optional
from database import DatabaseHelper


class Attendance:
    """Database operations for event attendance."""

    @staticmethod
    def check_in(user_id: int, event_id: int) -> int:
        """
        Marks a user as checked in (attended = 1) for a specific event.
        Inserts a new record or updates an existing one using an UPSERT query.
        """
        query = """
            INSERT INTO Attendance (user_id, event_id, attended, check_in_time)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, event_id) DO UPDATE SET
                attended = 1,
                check_in_time = CURRENT_TIMESTAMP
        """
        return DatabaseHelper.execute_write(query, (user_id, event_id))

    @staticmethod
    def get_by_user_and_event(user_id: int, event_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetches an attendance record for a specific user and event.
        """
        query = """
            SELECT * FROM Attendance
            WHERE user_id = ? AND event_id = ?
        """
        return DatabaseHelper.execute_query_one(query, (user_id, event_id))

    @staticmethod
    def get_for_event(event_id: int) -> List[Dict[str, Any]]:
        """
        Returns all attendance records for a specific event, including user details.
        """
        query = """
            SELECT 
                Attendance.attendance_id,
                Attendance.user_id,
                Attendance.event_id,
                Attendance.attended,
                Attendance.check_in_time,
                Users.name,
                Users.email
            FROM Attendance
            JOIN Users ON Attendance.user_id = Users.user_id
            WHERE Attendance.event_id = ?
            ORDER BY Users.name
        """
        return DatabaseHelper.execute_query(query, (event_id,))

    @staticmethod
    def get_for_user(user_id: int) -> List[Dict[str, Any]]:
        """
        Returns all events a user has attended or has attendance records for.
        """
        query = """
            SELECT 
                Attendance.attendance_id,
                Attendance.user_id,
                Attendance.event_id,
                Attendance.attended,
                Attendance.check_in_time,
                Events.title,
                Events.event_date,
                Events.event_time,
                Events.location
            FROM Attendance
            JOIN Events ON Attendance.event_id = Events.event_id
            WHERE Attendance.user_id = ?
            ORDER BY Events.event_date DESC, Events.event_time DESC
        """
        return DatabaseHelper.execute_query(query, (user_id,))

    @staticmethod
    def update_attendance(user_id: int, event_id: int, attended: bool) -> int:
        """
        Updates the attendance status (attended = 1 or 0) for a user at an event.
        """
        att_val = 1 if attended else 0
        query = """
            INSERT INTO Attendance (user_id, event_id, attended, check_in_time)
            VALUES (?, ?, ?, CASE WHEN ? = 1 THEN CURRENT_TIMESTAMP ELSE NULL END)
            ON CONFLICT(user_id, event_id) DO UPDATE SET
                attended = excluded.attended,
                check_in_time = excluded.check_in_time
        """
        return DatabaseHelper.execute_write(query, (user_id, event_id, att_val, att_val))

    @staticmethod
    def delete(user_id: int, event_id: int) -> int:
        """Deletes an attendance record."""
        query = "DELETE FROM Attendance WHERE user_id = ? AND event_id = ?"
        return DatabaseHelper.execute_write(query, (user_id, event_id))
