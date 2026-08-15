from datetime import datetime
import re
from typing import Optional, Tuple


class ValidationService:
    """Utility service for strict input validation, format checking, and sanitization."""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validates if an email string conforms to standard RFC 5322 format."""
        if not email or not isinstance(email, str):
            return False
        return bool(ValidationService.EMAIL_REGEX.match(email.strip()))

    @staticmethod
    def validate_event_date_and_time(
        event_date_str: str,
        event_time_str: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates event date and time strings.
        Ensures date format is YYYY-MM-DD, time format is HH:MM or HH:MM:SS,
        and that the event is not scheduled in the past.
        """
        if not event_date_str or not event_time_str:
            return False, "event_date and event_time are required"

        # 1. Parse date
        try:
            parsed_date = datetime.strptime(event_date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid event_date format. Expected YYYY-MM-DD"

        # 2. Parse time
        parsed_time = None
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                parsed_time = datetime.strptime(event_time_str.strip(), fmt).time()
                break
            except ValueError:
                continue

        if not parsed_time:
            return False, "Invalid event_time format. Expected HH:MM or HH:MM:SS"

        # 3. Combine and check if in the past
        event_dt = datetime.combine(parsed_date, parsed_time)

        # Allow today's date if event time has not passed, or block past dates
        current_dt = datetime.now()

        if event_dt < current_dt:
            return False, "Event date and time cannot be in the past"

        return True, None

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Strips leading/trailing whitespace and truncates string to max_length."""
        if not value:
            return ""
        return str(value).strip()[:max_length]
