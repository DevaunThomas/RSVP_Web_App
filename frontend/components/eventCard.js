import {
  resolveEventStatus
} from "../utils/eventStatus.js";

const statusLabels = {
  open: "Open",
  full: "Full",
  canceled: "Canceled",
  past: "Past",
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatEventDate(dateString) {
  const date = new Date(`${dateString}T00:00:00`);

  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
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

export function renderEventCard(event) {
  if (!event?.id || !event?.title || !event?.date) {
    console.error("Cannot render an event card with missing event data.", event);
    return "";
  }

  const status = resolveEventStatus(event);
  const remainingSpots = Math.max(event.capacity - event.rsvpCount, 0);

  const capacityText =
    status === "full"
      ? "Event is full"
      : `${remainingSpots} ${
          remainingSpots === 1 ? "spot" : "spots"
        } remaining`;

  const eventTime = event.endTime
    ? `${formatEventTime(event.startTime)} – ${formatEventTime(event.endTime)}`
    : formatEventTime(event.startTime);

    
  // Builds one reusable card for the event listing
  return `
    <article
      class="event-card"
      aria-labelledby="event-title-${escapeHtml(event.id)}"
      data-event-id="${escapeHtml(event.id)}"
    >
      <div class="event-card__header">
        <span class="event-card__date">
          ${escapeHtml(formatEventDate(event.date))}
        </span>

        <span class="status-badge status-badge--${status}">
          ${statusLabels[status]}
        </span>
      </div>

      <div class="event-card__body">
        <h2 class="event-card__title" id="event-title-${escapeHtml(event.id)}">
          ${escapeHtml(event.title)}
        </h2>

        <dl class="event-card__details">
          <div class="event-card__detail">
            <dt>Time</dt>
            <dd>${escapeHtml(eventTime)}</dd>
          </div>

          <div class="event-card__detail">
            <dt>Location</dt>
            <dd>${escapeHtml(event.location)}</dd>
          </div>

          <div class="event-card__detail">
            <dt>Organizer</dt>
            <dd>${escapeHtml(event.organizer)}</dd>
          </div>
        </dl>
      </div>

      <div class="event-card__footer">
        <span class="event-card__capacity">
          ${escapeHtml(capacityText)}
        </span>

        <a
          class="button button--primary"
          href="#/event/${escapeHtml(event.id)}"
          aria-label="View details for ${escapeHtml(event.title)}"
        >
          View Details
        </a>
      </div>
    </article>
  `;
}