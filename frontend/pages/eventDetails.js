import { mockEvents } from "../data/mockEvents.js";

function formatEventDate(dateString) {
  const date = new Date(`${dateString}T00:00:00`);

  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function formatEventTime(timeString) {
  const [hours, minutes] = timeString.split(":").map(Number);
  const date = new Date(2000, 0, 1, hours, minutes);

  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export function renderEventDetails(mainContent, eventId) {
  // Find the selected event using the ID from the URL.
  const event = mockEvents.find((event) => event.id === Number(eventId));

  if (!event) {
    mainContent.innerHTML = `
      <section class="container message-state event-not-found">
        <h2>Event Not Found</h2>
        <p>The event you're looking for doesn't exist.</p>
        <a href="#" class="button button--primary">Back to Events</a>
      </section>
    `;
    return;
  }

  // Calculate availability from the event capacity.
  const remainingSpots = Math.max(event.capacity - event.rsvpCount, 0);
  const isUnavailable =
    event.status === "full" ||
    event.status === "canceled" ||
    event.status === "past" ||
    remainingSpots === 0;

  const eventTime = event.endTime
    ? `${formatEventTime(event.startTime)} – ${formatEventTime(event.endTime)}`
    : formatEventTime(event.startTime);

  mainContent.innerHTML = `
    <section class="container event-details">
      <a href="#" class="back-link">← Back to Events</a>

      <header class="event-details__header">
      <span class="status-badge status-badge--${event.status}">
        ${event.status.charAt(0).toUpperCase() + event.status.slice(1)}
      </span>

        <h1>${event.title}</h1>

        <p class="event-details__description">
          ${event.description}
        </p>
      </header>

      <section class="event-details__info" aria-label="Event information">
        <p>
          <strong>Date:</strong>
          ${formatEventDate(event.date)}
        </p>

        <p>
          <strong>Time:</strong>
          ${eventTime}
        </p>

        <p>
          <strong>Location:</strong>
          ${event.location}
        </p>

        <p>
          <strong>Organizer:</strong>
          ${event.organizer}
        </p>

        <p>
          <strong>Spots Remaining:</strong>
          ${remainingSpots}
        </p>
      </section>

      <button
        type="button"
        class="button button--primary"
        ${isUnavailable ? "disabled" : ""}
      >
        ${isUnavailable ? "RSVP Unavailable" : "RSVP"}
      </button>
    </section>
  `;
}