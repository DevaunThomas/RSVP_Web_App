import { getCurrentUser } from "../utils/session.js";

const API_BASE_URL = "http://127.0.0.1:5000/api";

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
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function formatEventTime(timeString) {
  const [hours, minutes] = timeString
    .split(":")
    .map(Number);

  const date = new Date();
  date.setHours(hours, minutes, 0, 0);

  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function renderError(mainContent, message) {
  mainContent.innerHTML = `
    <section class="page-section">
      <div class="state-message state-message--error">
        <h1>Attendees could not be loaded</h1>
        <p>${escapeHtml(message)}</p>

        <a href="#/dashboard" class="button button--primary">
          Return to Dashboard
        </a>
      </div>
    </section>
  `;
}

function renderAttendeeRow(
  rsvp,
  attended,
  eventIsCanceled
) {
  const isRegistered =
    rsvp.rsvp_status === "Registered";

  let attendanceControl = `
    <span class="attendee-table__not-eligible">
      Not eligible
    </span>
  `;

  if (isRegistered) {
    attendanceControl = `
      <button
        type="button"
        class="button ${
          attended
            ? "button--secondary"
            : "button--primary"
        }"
        data-attendance-user-id="${Number(rsvp.user_id)}"
        data-attended="${attended}"
        ${eventIsCanceled ? "disabled" : ""}
      >
        ${
          attended
            ? "Undo Check-in"
            : "Check In"
        }
      </button>
    `;
  }

  return `
    <tr>
      <td data-label="Name">
        ${escapeHtml(rsvp.name)}
      </td>

      <td data-label="Email">
        ${escapeHtml(rsvp.email)}
      </td>

      <td data-label="RSVP Status">
        <span
          class="status-badge status-badge--${rsvp.rsvp_status.toLowerCase()}"
        >
          ${escapeHtml(rsvp.rsvp_status)}
        </span>
      </td>

      <td data-label="Attendance">
        ${
          attended
            ? `
              <span class="status-badge status-badge--attended">
                Checked In
              </span>
            `
            : `
              <span class="status-badge status-badge--not-attended">
                Not Checked In
              </span>
            `
        }
      </td>

      <td data-label="Action">
        ${attendanceControl}
      </td>
    </tr>
  `;
}

export async function renderManageAttendees(
  mainContent,
  eventId
) {
  const currentUser = getCurrentUser();
  const numericEventId = Number(eventId);

  if (!currentUser) {
    window.location.hash = "#/login";
    return;
  }

  if (currentUser.role !== "organizer") {
    renderError(
      mainContent,
      "Only organizers can manage event attendees."
    );
    return;
  }

  if (
    !Number.isInteger(numericEventId) ||
    numericEventId <= 0
  ) {
    renderError(mainContent, "Invalid event identifier.");
    return;
  }

  mainContent.innerHTML = `
    <section class="page-section">
      <div class="state-message">
        <h1>Loading attendees...</h1>
      </div>
    </section>
  `;

  try {
    const eventResponse = await fetch(
      `${API_BASE_URL}/events/${numericEventId}`
    );

    const event = await eventResponse.json();

    if (!eventResponse.ok) {
      throw new Error(
        event.error || "Unable to load the event."
      );
    }

    const isEventOwner =
      Number(event.organizer_id) ===
      Number(currentUser.user_id);

    if (!isEventOwner) {
      renderError(
        mainContent,
        "You can only manage attendees for events you created."
      );
      return;
    }

    const [rsvpResponse, attendanceResponse] =
      await Promise.all([
        fetch(
          `${API_BASE_URL}/events/${numericEventId}/rsvps`
        ),
        fetch(
          `${API_BASE_URL}/events/${numericEventId}/attendance`
        ),
      ]);

    const rsvps = await rsvpResponse.json();
    const attendance = await attendanceResponse.json();

    if (!rsvpResponse.ok) {
      throw new Error(
        rsvps.error || "Unable to load event RSVPs."
      );
    }

    if (!attendanceResponse.ok) {
      throw new Error(
        attendance.error ||
          "Unable to load attendance records."
      );
    }

    const activeRsvps = rsvps.filter(
      (rsvp) => rsvp.rsvp_status !== "Canceled"
    );

    const attendanceByUserId = new Map(
      attendance.map((record) => [
        Number(record.user_id),
        Boolean(record.attended),
      ])
    );

    const registeredCount = activeRsvps.filter(
      (rsvp) => rsvp.rsvp_status === "Registered"
    ).length;

    const waitlistedCount = activeRsvps.filter(
      (rsvp) => rsvp.rsvp_status === "Waitlisted"
    ).length;

    const checkedInCount = activeRsvps.filter(
      (rsvp) =>
        attendanceByUserId.get(Number(rsvp.user_id))
    ).length;

    const eventIsCanceled =
      event.status === "Canceled";

    mainContent.innerHTML = `
      <section class="page-section attendee-management">
        <a
          href="#/event/${numericEventId}"
          class="back-link"
        >
          &larr; Back to Event
        </a>

        <div class="attendee-management__header">
          <div>
            <h1>Manage Attendees</h1>
            <h2>${escapeHtml(event.title)}</h2>

            <p>
              ${escapeHtml(formatEventDate(event.event_date))}
              at
              ${escapeHtml(formatEventTime(event.event_time))}
            </p>
          </div>

          ${
            eventIsCanceled
              ? `
                <span class="status-badge status-badge--canceled">
                  Event Canceled
                </span>
              `
              : ""
          }
        </div>

        <div class="attendee-summary">
          <article class="attendee-summary__card">
            <span>Registered</span>
            <strong>${registeredCount}</strong>
          </article>

          <article class="attendee-summary__card">
            <span>Waitlisted</span>
            <strong>${waitlistedCount}</strong>
          </article>

          <article class="attendee-summary__card">
            <span>Checked In</span>
            <strong>${checkedInCount}</strong>
          </article>
        </div>

        ${
          eventIsCanceled
            ? `
              <div class="form-message form-message--error">
                Attendance cannot be changed for a canceled event.
              </div>
            `
            : ""
        }

        <div class="attendee-table-wrapper">
          ${
            activeRsvps.length === 0
              ? `
                <div class="state-message">
                  <h2>No active RSVPs</h2>
                  <p>
                    Registered and waitlisted students will appear here.
                  </p>
                </div>
              `
              : `
                <table class="attendee-table">
                  <thead>
                    <tr>
                      <th scope="col">Name</th>
                      <th scope="col">Email</th>
                      <th scope="col">RSVP Status</th>
                      <th scope="col">Attendance</th>
                      <th scope="col">Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    ${activeRsvps
                      .map((rsvp) =>
                        renderAttendeeRow(
                          rsvp,
                          attendanceByUserId.get(
                            Number(rsvp.user_id)
                          ) || false,
                          eventIsCanceled
                        )
                      )
                      .join("")}
                  </tbody>
                </table>
              `
          }
        </div>
      </section>
    `;

    const attendanceButtons =
      mainContent.querySelectorAll(
        "[data-attendance-user-id]"
      );

    attendanceButtons.forEach((button) => {
      button.addEventListener("click", async () => {
        const userId = Number(
          button.dataset.attendanceUserId
        );

        const currentlyAttended =
          button.dataset.attended === "true";

        button.disabled = true;
        button.textContent = "Saving...";

        try {
          const response = await fetch(
            `${API_BASE_URL}/events/${numericEventId}/attendance/${userId}`,
            {
              method: "PATCH",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                attended: !currentlyAttended,
              }),
            }
          );

          const result = await response.json();

          if (!response.ok) {
            throw new Error(
              result.error ||
                "Unable to update attendance."
            );
          }

          await renderManageAttendees(
            mainContent,
            numericEventId
          );
        } catch (error) {
          window.alert(error.message);

          button.disabled = false;
          button.textContent = currentlyAttended
            ? "Undo Check-in"
            : "Check In";
        }
      });
    });
  } catch (error) {
    renderError(mainContent, error.message);
  }
}