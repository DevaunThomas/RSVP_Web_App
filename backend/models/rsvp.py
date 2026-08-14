from typing import Any, Dict, List, Optional

from database import DatabaseHelper


class RSVP:
    """Database operations for event RSVPs."""

    @staticmethod
    def create(
        user_id: int,
        event_id: int,
        rsvp_status: str = "Registered"
    ) -> int:
        query = """
            INSERT INTO RSVPs (user_id, event_id, rsvp_status)
            VALUES (?, ?, ?)
        """

        return DatabaseHelper.execute_write(
            query,
            (user_id, event_id, rsvp_status)
        )

    @staticmethod
    def get_by_id(rsvp_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT *
            FROM RSVPs
            WHERE rsvp_id = ?
        """

        return DatabaseHelper.execute_query_one(query, (rsvp_id,))

    @staticmethod
    def get_by_user_and_event(
        user_id: int,
        event_id: int
    ) -> Optional[Dict[str, Any]]:
        query = """
            SELECT *
            FROM RSVPs
            WHERE user_id = ?
              AND event_id = ?
        """

        return DatabaseHelper.execute_query_one(
            query,
            (user_id, event_id)
        )

    @staticmethod
    def get_for_user(user_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT
                RSVPs.rsvp_id,
                RSVPs.user_id,
                RSVPs.event_id,
                RSVPs.rsvp_status,
                RSVPs.rsvp_date,
                Events.title,
                Events.event_date,
                Events.event_time,
                Events.location,
                Events.status AS event_status
            FROM RSVPs
            JOIN Events
                ON RSVPs.event_id = Events.event_id
            WHERE RSVPs.user_id = ?
            ORDER BY Events.event_date, Events.event_time
        """

        return DatabaseHelper.execute_query(query, (user_id,))

    @staticmethod
    def get_for_event(event_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT
                RSVPs.rsvp_id,
                RSVPs.rsvp_status,
                RSVPs.rsvp_date,
                Users.user_id,
                Users.name,
                Users.email
            FROM RSVPs
            JOIN Users
                ON RSVPs.user_id = Users.user_id
            WHERE RSVPs.event_id = ?
            ORDER BY Users.name
        """

        return DatabaseHelper.execute_query(query, (event_id,))

    @staticmethod
    def update_status(rsvp_id: int, rsvp_status: str) -> int:
        query = """
            UPDATE RSVPs
            SET rsvp_status = ?
            WHERE rsvp_id = ?
        """

        return DatabaseHelper.execute_write(
            query,
            (rsvp_status, rsvp_id)
        )

    @staticmethod
    def update_status_by_user_and_event(
        user_id: int,
        event_id: int,
        rsvp_status: str
    ) -> int:
        query = """
            UPDATE RSVPs
            SET rsvp_status = ?
            WHERE user_id = ?
              AND event_id = ?
        """

        return DatabaseHelper.execute_write(
            query,
            (rsvp_status, user_id, event_id)
        )

    @staticmethod
    def delete(rsvp_id: int) -> int:
        query = "DELETE FROM RSVPs WHERE rsvp_id = ?"
        return DatabaseHelper.execute_write(query, (rsvp_id,))

    @staticmethod
    def get_next_waitlisted(event_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT rsvp_id, user_id, event_id, rsvp_status, rsvp_date
            FROM RSVPs
            WHERE event_id = ? AND rsvp_status = 'Waitlisted'
            ORDER BY rsvp_date ASC, rsvp_id ASC
            LIMIT 1
        """
        return DatabaseHelper.execute_query_one(query, (event_id,))