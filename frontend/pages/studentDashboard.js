import { renderEventCard } from "../components/eventCard.js";
import { mockEvents } from "../data/mockEvents.js";

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

// Render the student dashboard page
export function renderStudentDashboard(mainContent) {
  const upcomingEvents = sortEventsByDate(mockEvents).slice(0, 3);

  mainContent.innerHTML = `
    <section class="dashboard-page">
      <div class="dashboard-header">
        <h1>Student Dashboard</h1>
        <p>
          Welcome back! Browse upcoming events and manage your RSVPs.
        </p>
      </div>

      <div class="dashboard-grid">
        <section class="dashboard-card">
          <div class="dashboard-card__header">
            <h2>Upcoming Events</h2>
            <a href="#/" class="dashboard-link">View all events</a>
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

          <div class="dashboard-list">
            <p>You haven't RSVP'd to any events yet.</p>
          </div>
        </section>
      </div>
    </section>
  `;
}