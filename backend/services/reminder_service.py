import logging
from typing import List, Dict, Any
from database import DatabaseHelper
from models.event import Event
from models.rsvp import RSVP
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class ReminderService:
    """Service to scan upcoming events and dispatch reminder notifications."""

    @staticmethod
    def check_and_send_reminders() -> int:
        """
        Scans all active events and dispatches reminder notifications
        to registered attendees who have not yet received a reminder.
        """
        active_events = Event.get_active()
        reminders_sent = 0

        for event in active_events:
            event_id = event["event_id"]
            title = event["title"]
            event_date = event["event_date"]
            event_time = event["event_time"]

            rsvps = RSVP.get_for_event(event_id)

            for rsvp in rsvps:
                if rsvp.get("rsvp_status") == "Registered":
                    user_id = rsvp["user_id"]

                    # Check if reminder already sent to this user for this event
                    existing = DatabaseHelper.execute_query_one(
                        """
                        SELECT notification_id FROM Notifications
                        WHERE user_id = ? AND event_id = ? AND notification_type = 'Reminder'
                        """,
                        (user_id, event_id)
                    )

                    if not existing:
                        NotificationService.notify_event_reminder(
                            user_id=user_id,
                            event_id=event_id,
                            event_title=title,
                            event_date=event_date,
                            event_time=event_time
                        )
                        reminders_sent += 1

        return reminders_sent

    @staticmethod
    def init_scheduler(app=None):
        """Initializes the background scheduler for reminder checks."""
        # Avoid running background scheduler during test runs
        if app and app.config.get("TESTING"):
            return None

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            scheduler = BackgroundScheduler(daemon=True)
            # Run reminder check every hour
            scheduler.add_job(
                ReminderService.check_and_send_reminders,
                "interval",
                hours=1,
                id="event_reminder_job",
                replace_existing=True
            )
            scheduler.start()
            logger.info("Reminder background scheduler started.")
            return scheduler
        except Exception as e:
            logger.error(f"Failed to start reminder scheduler: {e}")
            return None
