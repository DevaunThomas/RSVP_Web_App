import { renderEventCard } from "../components/eventCard.js";
import { getCurrentUser } from "../utils/session.js";
import { resolveEventStatus } from "../utils/eventStatus.js";

function sortEventsByDate(events) {
  return [...events].sort((firstEvent, secondEvent) => {
    const firstDate = new Date(
      `${firstEvent.date}T${firstEvent.startTime || "00:00"}`
    );

    const secondDate = new Date(
      `${secondEvent.date}T${secondEvent.startTime || "00:00"}`
    );

    return firstDate - secondDate;
  });
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

// Render the student dashboard page
export async function renderStudentDashboard(mainContent) {
  const currentUser = getCurrentUser();
  
  if (!currentUser) {
    window.location.hash = "#/login";
    return;
  }
  
  if (currentUser.role !== "student") {
    window.location.hash = "#/organizer-dashboard";
    return;
  }

  try {
    // Load all events
    const eventsResponse = await fetch(
      "http://127.0.0.1:5000/api/events"
    );

    if (!eventsResponse.ok) {
      throw new Error("Failed to load events.");
    }

    const apiEvents = await eventsResponse.json();

    const dashboardEvents = apiEvents.map((event) => ({
      id: event.event_id,
      title: event.title,
      description: event.description || "",
      date: event.event_date,
      startTime: event.event_time,
      endTime: event.end_time || null,
      location: event.location,
      organizer:
        event.organizer_name || "Unknown organizer",
      capacity: Number(event.capacity) || 0,
      rsvpCount: Number(event.registered_count) || 0,
      status: event.status || "Active",
    }));

    const upcomingEvents = sortEventsByDate(
      dashboardEvents
        .map((event) => ({
          ...event,
          status: resolveEventStatus(event),
        }))
        .filter((event) => event.status !== "past")
    ).slice(0, 3);

    // Load student's RSVPs
    const response = await fetch(
      `http://127.0.0.1:5000/api/users/${currentUser.user_id}/rsvps`
    );

    if (!response.ok) {
      throw new Error("Failed to load student RSVPs.");
    }

    const rsvps = await response.json();

    const activeRsvps = rsvps.filter(
      (rsvp) => rsvp.rsvp_status !== "Canceled"
    );

    mainContent.innerHTML = `
      <section class="dashboard-page">
        <div class="dashboard-header">
          <h1>Student Dashboard</h1>

          <p>
            Welcome back, ${currentUser.name}! Browse upcoming events and manage your RSVPs.
          </p>
        </div>

        <div class="dashboard-grid">

          <section class="dashboard-card">
            <div class="dashboard-card__header">
              <h2>Upcoming Events</h2>

              <a href="#/events" class="button button--primary">
                View all events
              </a>
            </div>

            <div class="event-grid">
              ${
                upcomingEvents.length > 0
                  ? upcomingEvents.map(renderEventCard).join("")
                  : "<p>No upcoming events available.</p>"
              }
            </div>
          </section>

          <section class="dashboard-card">
            <h2>My RSVPs</h2>

            <div class="rsvp-grid">
              ${
                activeRsvps.length > 0
                  ? activeRsvps
                      .map(
                        (rsvp) => `
                          <article class="rsvp-card">
                            <div class="rsvp-card__body">
                              <h3 class="rsvp-card__title">
                                ${rsvp.title}
                              </h3>

                              <dl class="rsvp-card__details">
                                <div class="rsvp-card__detail">
                                  <dt>Date</dt>
                                  <dd>${formatEventDate(rsvp.event_date)}</dd>
                                </div>

                                <div class="rsvp-card__detail">
                                  <dt>Time</dt>
                                  <dd>${formatEventTime(rsvp.event_time)}</dd>
                                </div>

                                <div class="rsvp-card__detail">
                                  <dt>Location</dt>
                                  <dd>${rsvp.location}</dd>
                                </div>

                                <div class="rsvp-card__detail">
                                  <dt>Status</dt>
                                  <dd>
                                    <span
                                      class="rsvp-status rsvp-status--${rsvp.rsvp_status.toLowerCase()}"
                                    >
                                      ${rsvp.rsvp_status}
                                    </span>
                                  </dd>
                                </div>

                              </dl>
                            </div>

                            <div class="rsvp-card__footer">
                              <div class="dashboard-list__actions">
                                <a
                                  href="#/event/${rsvp.event_id}"
                                  class="button button--primary"
                                >
                                  View Event
                                </a>

                                ${
                                  [
                                    "Registered",
                                    "Waitlisted",
                                  ].includes(rsvp.rsvp_status)
                                    ? `
                                      <button
                                        class="button button--secondary cancel-rsvp-button"
                                        type="button"
                                        data-rsvp-id="${rsvp.rsvp_id}"
                                      >
                                        Cancel RSVP
                                      </button>
                                    `
                                    : ""
                                }
                              </div>
                            </div>
                          </article>
                        `
                      )
                      .join("")
                  : "<p>You haven't RSVP'd to any events yet.</p>"
              }
            </div>
          </section>

        </div>
      </section>
    `;

    const cancelButtons = mainContent.querySelectorAll(
      ".cancel-rsvp-button"
    );

    cancelButtons.forEach((cancelButton) => {
      cancelButton.addEventListener("click", async () => {
        const rsvpId = cancelButton.dataset.rsvpId;

        if (!rsvpId) {
          console.error("RSVP ID was not found.");
          return;
        }

        const confirmed = window.confirm(
          "Are you sure you want to cancel your RSVP?"
        );

        if (!confirmed) {
          return;
        }

        cancelButton.disabled = true;
        cancelButton.textContent = "Canceling...";

        try {
          const response = await fetch(
            `http://127.0.0.1:5000/api/rsvps/${rsvpId}/cancel`,
            {
              method: "PATCH",
            }
          );

          const data = await response.json();

          if (!response.ok) {
            throw new Error(
              data.error || "Unable to cancel RSVP."
            );
          }

          alert("RSVP canceled successfully.");

          await renderStudentDashboard(mainContent);
        } catch (error) {
          console.error("Failed to cancel RSVP.", error);
          alert(error.message);

          cancelButton.disabled = false;
          cancelButton.textContent = "Cancel RSVP";
        }
      });
    });
  } catch (error) {
    console.error(error);

    mainContent.innerHTML = `
      <section class="dashboard-page">
        <h2>Unable to load dashboard.</h2>

        <p>Please try again later.</p>
      </section>
    `;
  }
}