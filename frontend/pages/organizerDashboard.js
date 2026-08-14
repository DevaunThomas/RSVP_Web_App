import { renderEventCard } from "../components/eventCard.js";
import { getCurrentUser } from "../utils/session.js";
import { authenticatedFetch } from "../utils/api.js";

function sortRsvpsByDate(rsvps) {
  return [...rsvps].sort(
    (firstRsvp, secondRsvp) =>
      new Date(secondRsvp.rsvp_date) -
      new Date(firstRsvp.rsvp_date)
  );
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatEventDate(dateString) {
  const date = new Date(`${dateString}T00:00:00`);

  return new Intl.DateTimeFormat("en-US", {
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

function formatRsvpDate(dateTimeString) {
  const date = new Date(dateTimeString.replace(" ", "T"));

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

// Render the organizer dashboard page
export async function renderOrganizerDashboard(mainContent) {

  const currentUser = getCurrentUser();
  
  if (!currentUser) {
    window.location.hash = "#/login";
    return;
  }

  if (currentUser.role !== "organizer") {
    window.location.hash = "#/student-dashboard";
    return;
  }

  try {
    const eventsResponse = await authenticatedFetch(
      `http://127.0.0.1:5000/api/organizers/${currentUser.user_id}/events`
    );

    if (!eventsResponse.ok) {
      throw new Error("Failed to load organizer events.");
    }

    const apiEvents = await eventsResponse.json();

    // Convert backend event fields into the format used by event cards.
    const events = apiEvents.map((event) => ({
      id: event.event_id,
      title: event.title,
      description: event.description || "",
      date: event.event_date,
      startTime: event.event_time,
      endTime: event.end_time || null,
      location: event.location,
      organizer: currentUser.name,
      capacity: Number(event.capacity) || 0,
      rsvpCount: Number(event.registered_count) || 0,
      status:
        event.status?.toLowerCase() === "active"
          ? "open"
          : event.status?.toLowerCase() || "open",
    }));

    // Load the RSVPs for every organizer event.
    const rsvpResponses = await Promise.all(
      apiEvents.map(async (event) => {
        const response = await authenticatedFetch(
          `http://127.0.0.1:5000/api/events/${event.event_id}/rsvps`
        );

        if (!response.ok) {
          throw new Error(
            `Failed to load RSVPs for event ${event.event_id}.`
          );
        }

        const eventRsvps = await response.json();

        return eventRsvps.map((rsvp) => ({
          ...rsvp,
          event_id: event.event_id,
          event_title: event.title,
        }));
      })
    );

    const recentRsvps = sortRsvpsByDate(
      rsvpResponses.flat()
    ).slice(0, 5);

    mainContent.innerHTML = `
      <section class="dashboard-page">
        <div class="dashboard-header">
          <h1>Organizer Dashboard</h1>

          <p>
            Welcome back, ${escapeHtml(currentUser.name)}! Manage your campus events
            and monitor attendee registrations.
          </p>
        </div>

        <div class="dashboard-grid">
          <section class="dashboard-card">
            <div class="dashboard-card__header">
              <h2>My Events</h2>

              <a
                href="#/create-event"
                class="button dashboard-action"
              >
                Create Event
              </a>
            </div>

            <div class="event-grid">
              ${
                events.length > 0
                  ? events.map(renderEventCard).join("")
                  : "<p>You haven't created any events yet.</p>"
              }
            </div>
          </section>

          <section class="dashboard-card">
            <h2>Recent RSVPs</h2>

            <div class="rsvp-grid">
              ${
                recentRsvps.length > 0
                  ? recentRsvps
                      .map(
                        (rsvp) => `
                          <article class="rsvp-card">
                            <div class="rsvp-card__body">
                              <h3 class="rsvp-card__title">
                                ${escapeHtml(rsvp.name)}
                              </h3>

                              <dl class="rsvp-card__details">
                                <div class="rsvp-card__detail">
                                  <dt>Event</dt>
                                  <dd>${escapeHtml(rsvp.event_title)}</dd>
                                </div>

                                <div class="rsvp-card__detail">
                                  <dt>Email</dt>
                                  <dd>${escapeHtml(rsvp.email)}</dd>
                                </div>

                                <div class="rsvp-card__detail">
                                  <dt>Status</dt>
                                  <dd>
                                    <span
                                      class="rsvp-status rsvp-status--${rsvp.rsvp_status.toLowerCase()}"
                                    >
                                      ${escapeHtml
                                        ? escapeHtml(rsvp.rsvp_status)
                                        : rsvp.rsvp_status}
                                    </span>
                                  </dd>
                                </div>

                                <div class="rsvp-card__detail">
                                  <dt>RSVP Date</dt>
                                  <dd>${escapeHtml(formatRsvpDate(rsvp.rsvp_date))}</dd>
                                </div>
                              </dl>
                            </div>

                            <div class="rsvp-card__footer">
                              <a
                                href="#/event/${rsvp.event_id}"
                                class="button button--primary"
                              >
                                View Event
                              </a>
                            </div>
                          </article>
                        `
                      )
                      .join("")
                  : "<p>No attendee registrations yet.</p>"
              }
            </div>
          </section>
        </div>
      </section>
    `;
  } catch (error) {
    console.error(
      "Failed to render organizer dashboard.",
      error
    );

    mainContent.innerHTML = `
      <section class="dashboard-page">
        <div class="dashboard-card">
          <h2>Unable to load organizer dashboard</h2>
          <p>Please refresh the page and try again.</p>
        </div>
      </section>
    `;
  }
}
