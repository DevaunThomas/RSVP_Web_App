import { getCurrentUser } from "../utils/session.js";
import {
  resolveEventStatus
} from "../utils/eventStatus.js";

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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderEventNotFound(mainContent) {
  mainContent.innerHTML = `
    <section class="container message-state event-not-found">
      <h2>Event Not Found</h2>
      <p>The event you're looking for doesn't exist.</p>

      <a href="#/events" class="button button--primary">
        Back to Events
      </a>
    </section>
  `;
}

function renderEventLoadError(mainContent) {
  mainContent.innerHTML = `
    <section class="container message-state" role="alert">
      <h2>Event Could Not Be Loaded</h2>
      <p>Please return to the Events page and try again.</p>

      <a href="#/events" class="button button--primary">
        Back to Events
      </a>
    </section>
  `;
}

export async function renderEventDetails(mainContent, eventId) {
  if (!mainContent) {
    console.error("The event details container was not found.");
    return;
  }

  const numericEventId = Number(eventId);

  if (!Number.isInteger(numericEventId) || numericEventId <= 0) {
    renderEventNotFound(mainContent);
    return;
  }

  const currentUser = getCurrentUser();

  mainContent.innerHTML = `
    <section class="page-loading" role="status" aria-live="polite">
      <p>Loading event details…</p>
    </section>
  `;

  try {
    const response = await fetch(
      `http://127.0.0.1:5000/api/events/${numericEventId}`
    );

    if (response.status === 404) {
      renderEventNotFound(mainContent);
      return;
    }

    if (!response.ok) {
      throw new Error("Failed to load event details.");
    }

    const apiEvent = await response.json();
    let existingRsvp = null;

    if (
      currentUser &&
      currentUser.role === "student"
    ) {
      const rsvpsResponse = await fetch(
        `http://127.0.0.1:5000/api/users/${currentUser.user_id}/rsvps`
      );

      if (!rsvpsResponse.ok) {
        throw new Error(
          "Failed to check your RSVP status."
        );
      }

      const userRsvps = await rsvpsResponse.json();

      existingRsvp = userRsvps.find(
        (rsvp) =>
          Number(rsvp.event_id) === numericEventId
      ) || null;
    }

    const event = {
      id: apiEvent.event_id,
      title: apiEvent.title,
      description: apiEvent.description || "No description provided.",
      date: apiEvent.event_date,
      startTime: apiEvent.event_time,
      endTime: apiEvent.end_time || null,
      location: apiEvent.location,
      organizer: apiEvent.organizer_name || "Unknown organizer",
      capacity: Number(apiEvent.capacity) || 0,
      rsvpCount: Number(apiEvent.registered_count) || 0,
      status: apiEvent.status || "Active",
    };

    event.status = resolveEventStatus(event);

    const isEventOwner =
      currentUser?.role === "organizer" &&
      Number(apiEvent.organizer_id) ===
        Number(currentUser.user_id);

    const remainingSpots = Math.max(
      event.capacity - event.rsvpCount,
      0
    );

    const isFull =
      event.status === "full" ||
      remainingSpots === 0;

    const isUnavailable =
      event.status === "canceled" ||
      event.status === "past";

      const activeRsvpStatus = [
        "Registered",
        "Waitlisted",
      ].includes(existingRsvp?.rsvp_status)
        ? existingRsvp.rsvp_status
        : null;

      const rsvpButtonIsDisabled =
        isUnavailable || Boolean(activeRsvpStatus);

      const rsvpButtonText =
        activeRsvpStatus ||
        (isUnavailable
          ? "RSVP Unavailable"
          : isFull
            ? "Join Waitlist"
            : "RSVP");

    const eventTime = event.endTime
      ? `${formatEventTime(event.startTime)} – ${formatEventTime(
          event.endTime
        )}`
      : formatEventTime(event.startTime);

    const statusLabel =
      event.status.charAt(0).toUpperCase() + event.status.slice(1);

    mainContent.innerHTML = `
      <section class="container event-details">
        <a href="#/events" class="back-link">← Back to Events</a>

        <header class="event-details__header">
          <span class="status-badge status-badge--${escapeHtml(
            event.status
          )}">
            ${escapeHtml(statusLabel)}
          </span>

          <h1>${escapeHtml(event.title)}</h1>

          <p class="event-details__description">
            ${escapeHtml(event.description)}
          </p>
        </header>

        <section
          class="event-details__info"
          aria-label="Event information"
        >
          <p>
            <strong>Date:</strong>
            ${escapeHtml(formatEventDate(event.date))}
          </p>

          <p>
            <strong>Time:</strong>
            ${escapeHtml(eventTime)}
          </p>

          <p>
            <strong>Location:</strong>
            ${escapeHtml(event.location)}
          </p>

          <p>
            <strong>Organizer:</strong>
            ${escapeHtml(event.organizer)}
          </p>

          <p>
            <strong>Spots Remaining:</strong>
            ${remainingSpots}
          </p>
        </section>
        ${
          isEventOwner
          ? apiEvent.status === "Canceled"
            ? `
              <div class="event-detail__actions">
                <a
                  href="#/manage-attendees/${numericEventId}"
                  class="button button--primary"
                >
                  View Attendees
                </a>

                <button
                  type="button"
                  class="button button--secondary"
                  disabled
                >
                  Event Canceled
                </button>
              </div>
            `
            : `
              <div class="event-detail__actions">
                <a
                  href="#/edit-event/${numericEventId}"
                  class="button button--primary"
                >
                  Edit Event
                </a>

                <a
                  href="#/manage-attendees/${numericEventId}"
                  class="button button--secondary"
                >
                  Manage Attendees
                </a>

                <button
                  type="button"
                  id="cancel-event-button"
                  class="button button--danger"
                >
                  Cancel Event
                </button>
              </div>
            `
          : `
              <button
                type="button"
                id="rsvp-button"
                class="button button--primary"
                ${rsvpButtonIsDisabled ? "disabled" : ""}
              >
                ${escapeHtml(rsvpButtonText)}
              </button>
            `
        }
      </section>
    `;
    const cancelEventButton = mainContent.querySelector(
      "#cancel-event-button"
    );

    if (cancelEventButton) {
      cancelEventButton.addEventListener("click", async () => {
        const confirmed = window.confirm(
          "Are you sure you want to cancel this event? This action cannot be undone."
        );

        if (!confirmed) {
          return;
        }

        cancelEventButton.disabled = true;
        cancelEventButton.textContent = "Canceling...";

        try {
          const response = await fetch(
            `http://127.0.0.1:5000/api/events/${numericEventId}/cancel`,
            {
              method: "PATCH",
            }
          );

          const result = await response.json();

          if (!response.ok) {
            throw new Error(
              result.error || "Unable to cancel the event."
            );
          }

          window.alert("Event canceled successfully.");

          await renderEventDetails(
            mainContent,
            numericEventId
          );
        } catch (error) {
          window.alert(error.message);

          cancelEventButton.disabled = false;
          cancelEventButton.textContent = "Cancel Event";
        }
      });
    }

    const rsvpButton = mainContent.querySelector("#rsvp-button");

    if (
      rsvpButton &&
      !isUnavailable &&
      !activeRsvpStatus &&
      currentUser &&
      currentUser.role === "student"
    ) {
      rsvpButton.addEventListener("click", async () => {
        rsvpButton.disabled = true;
        rsvpButton.textContent = "Submitting...";
        
        try {
          const response = await fetch(
            "http://127.0.0.1:5000/api/rsvps",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              
              body: JSON.stringify({
                user_id: currentUser.user_id,
                event_id: numericEventId,
              }),
            }
          );
          
          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.error || "Failed to create RSVP.");
          }
          
          alert(
            data.rsvp_status === "Waitlisted"
            ? "You have been added to the waitlist."
            : "RSVP successful!"
          );
          
          renderEventDetails(mainContent, numericEventId);
        } catch (error) {
          alert(error.message);
          console.error("Failed to create RSVP.", error);

          rsvpButton.disabled = false;
          rsvpButton.textContent = isFull
            ? "Join Waitlist"
            : "RSVP";
        }
      });
    }

    if (
      rsvpButton &&
      !isUnavailable &&
      !activeRsvpStatus &&
      !currentUser
    ) {
      rsvpButton.textContent = "Log in to RSVP";

      rsvpButton.addEventListener("click", () => {
        window.location.hash = "#/login";
      });
    }

    if (
      rsvpButton &&
      !isUnavailable &&
      !activeRsvpStatus &&
      currentUser &&
      currentUser.role !== "student"
    ) {
      rsvpButton.disabled = true;
      rsvpButton.textContent = "Students Only";
    }

  } catch (error) {
    console.error("Failed to render event details.", error);
    renderEventLoadError(mainContent);
  }
}