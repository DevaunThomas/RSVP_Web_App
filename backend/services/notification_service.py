from typing import List
from models.notification import Notification
from models.rsvp import RSVP


class NotificationService:
    """Service handling notification dispatch logic for events and users."""

    @staticmethod
    def notify_event_update(event_id: int, event_title: str) -> int:
        """Sends an 'Update' notification to all registered and waitlisted attendees of an event."""
        rsvps = RSVP.get_for_event(event_id)
        count = 0

        for rsvp in rsvps:
            if rsvp.get("rsvp_status") in ("Registered", "Waitlisted"):
                Notification.create(
                    user_id=rsvp["user_id"],
                    event_id=event_id,
                    message=f"The event '{event_title}' has been updated.",
                    notification_type="Update"
                )
                count += 1

        return count

    @staticmethod
    def notify_event_cancellation(event_id: int, event_title: str) -> int:
        """Sends a 'Cancellation' notification to all registered and waitlisted attendees of an event."""
        rsvps = RSVP.get_for_event(event_id)
        count = 0

        for rsvp in rsvps:
            if rsvp.get("rsvp_status") in ("Registered", "Waitlisted"):
                Notification.create(
                    user_id=rsvp["user_id"],
                    event_id=event_id,
                    message=f"The event '{event_title}' has been canceled.",
                    notification_type="Cancellation"
                )
                count += 1

        return count

    @staticmethod
    def notify_waitlist_promotion(user_id: int, event_id: int, event_title: str) -> int:
        """Sends an 'Update' notification to a user when promoted off the waitlist."""
        return Notification.create(
            user_id=user_id,
            event_id=event_id,
            message=f"A spot opened up! You are now Registered for '{event_title}'.",
            notification_type="Update"
        )

    @staticmethod
    def notify_event_reminder(
        user_id: int,
        event_id: int,
        event_title: str,
        event_date: str,
        event_time: str
    ) -> int:
        """Sends a 'Reminder' notification to an attendee."""
        return Notification.create(
            user_id=user_id,
            event_id=event_id,
            message=f"Reminder: '{event_title}' is scheduled for {event_date} at {event_time}.",
            notification_type="Reminder"
        )
