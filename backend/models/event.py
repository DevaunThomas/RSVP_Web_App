from typing import Any, Dict, List, Optional

from database import DatabaseHelper


class Event:
    """Database operations for campus events."""

    @staticmethod
    def create(
        title: str,
        description: str,
        event_date: str,
        event_time: str,
        location: str,
        capacity: int,
        organizer_id: int
    ) -> int:
        query = """
            INSERT INTO Events (
                title,
                description,
                event_date,
                event_time,
                location,
                capacity,
                organizer_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        return DatabaseHelper.execute_write(
            query,
            (
                title,
                description,
                event_date,
                event_time,
                location,
                capacity,
                organizer_id
            )
        )

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        query = """
            SELECT
                Events.*,
                Users.name AS organizer_name
            FROM Events
            JOIN Users
                ON Events.organizer_id = Users.user_id
            ORDER BY event_date, event_time
        """

        return DatabaseHelper.execute_query(query)

    @staticmethod
    def get_active() -> List[Dict[str, Any]]:
        query = """
            SELECT
                Events.*,
                Users.name AS organizer_name
            FROM Events
            JOIN Users
                ON Events.organizer_id = Users.user_id
            WHERE Events.status != 'Canceled'
            ORDER BY event_date, event_time
        """

        return DatabaseHelper.execute_query(query)

    @staticmethod
    def get_by_id(event_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT
                Events.*,
                Users.name AS organizer_name
            FROM Events
            JOIN Users
                ON Events.organizer_id = Users.user_id
            WHERE Events.event_id = ?
        """

        return DatabaseHelper.execute_query_one(query, (event_id,))

    @staticmethod
    def get_by_organizer(organizer_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT *
            FROM Events
            WHERE organizer_id = ?
            ORDER BY event_date, event_time
        """

        return DatabaseHelper.execute_query(query, (organizer_id,))

    @staticmethod
    def update(
        event_id: int,
        title: str,
        description: str,
        event_date: str,
        event_time: str,
        location: str,
        capacity: int,
        status: str
    ) -> int:
        query = """
            UPDATE Events
            SET
                title = ?,
                description = ?,
                event_date = ?,
                event_time = ?,
                location = ?,
                capacity = ?,
                status = ?
            WHERE event_id = ?
        """

        return DatabaseHelper.execute_write(
            query,
            (
                title,
                description,
                event_date,
                event_time,
                location,
                capacity,
                status,
                event_id
            )
        )

    @staticmethod
    def cancel(event_id: int) -> int:
        query = """
            UPDATE Events
            SET status = 'Canceled'
            WHERE event_id = ?
        """

        return DatabaseHelper.execute_write(query, (event_id,))

    @staticmethod
    def delete(event_id: int) -> int:
        query = "DELETE FROM Events WHERE event_id = ?"
        return DatabaseHelper.execute_write(query, (event_id,))

    @staticmethod
    def get_registered_count(event_id: int) -> int:
        query = """
            SELECT COUNT(*) AS registered_count
            FROM RSVPs
            WHERE event_id = ?
              AND rsvp_status = 'Registered'
        """

        result = DatabaseHelper.execute_query_one(query, (event_id,))
        return result["registered_count"] if result else 0