from typing import Any, Dict, List, Optional

from database import DatabaseHelper


class User:
    """Database operations for users."""

    @staticmethod
    def create(
        name: str,
        email: str,
        password_hash: str,
        role: str
    ) -> int:
        query = """
            INSERT INTO Users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """

        return DatabaseHelper.execute_write(
            query,
            (name, email, password_hash, role)
        )

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        query = """
            SELECT user_id, name, email, role, created_at
            FROM Users
            ORDER BY user_id
        """

        return DatabaseHelper.execute_query(query)

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT user_id, name, email, role, created_at
            FROM Users
            WHERE user_id = ?
        """

        return DatabaseHelper.execute_query_one(query, (user_id,))

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT user_id, name, email, password_hash, role, created_at
            FROM Users
            WHERE email = ?
        """

        return DatabaseHelper.execute_query_one(query, (email,))

    @staticmethod
    def update(
        user_id: int,
        name: str,
        email: str,
        role: str
    ) -> int:
        query = """
            UPDATE Users
            SET name = ?, email = ?, role = ?
            WHERE user_id = ?
        """

        return DatabaseHelper.execute_write(
            query,
            (name, email, role, user_id)
        )

    @staticmethod
    def delete(user_id: int) -> int:
        query = "DELETE FROM Users WHERE user_id = ?"
        return DatabaseHelper.execute_write(query, (user_id,))