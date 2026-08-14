import { getCurrentUser } from "../utils/session.js";
import { authenticatedFetch } from "../utils/api.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderEditError(mainContent, message) {
  mainContent.innerHTML = `
    <section class="container message-state" role="alert">
      <h2>Unable to Edit Event</h2>
      <p>${escapeHtml(message)}</p>

      <a
        href="#/organizer-dashboard"
        class="button button--primary"
      >
        Back to Dashboard
      </a>
    </section>
  `;
}

export async function renderEditEvent(
  mainContent,
  eventId
) {
  const currentUser = getCurrentUser();

  if (!currentUser) {
    window.location.hash = "#/login";
    return;
  }

  if (currentUser.role !== "organizer") {
    window.location.hash = "#/student-dashboard";
    return;
  }

  const numericEventId = Number(eventId);

  if (
    !Number.isInteger(numericEventId) ||
    numericEventId <= 0
  ) {
    renderEditError(
      mainContent,
      "The selected event is invalid."
    );
    return;
  }

  mainContent.innerHTML = `
    <section
      class="page-loading"
      role="status"
      aria-live="polite"
    >
      <p>Loading event...</p>
    </section>
  `;

  try {
    const response = await fetch(
      `http://127.0.0.1:5000/api/events/${numericEventId}`
    );

    if (response.status === 404) {
      renderEditError(
        mainContent,
        "The selected event could not be found."
      );
      return;
    }

    if (!response.ok) {
      throw new Error("Failed to load the event.");
    }

    const event = await response.json();

    if (
      Number(event.organizer_id) !==
      Number(currentUser.user_id)
    ) {
      renderEditError(
        mainContent,
        "You can only edit events that you created."
      );
      return;
    }

    mainContent.innerHTML = `
      <section class="form-page">
        <div class="form-page__header">
          <h1>Edit Event</h1>
          <p>Update the event information below.</p>
        </div>

        <div class="form-card">
          <form
            id="edit-event-form"
            class="event-form"
            novalidate
          >
            <div class="form-group">
              <label for="edit-event-title">
                Event Title
              </label>

              <input
                type="text"
                id="edit-event-title"
                name="title"
                value="${escapeHtml(event.title)}"
                required
              />

              <p
                id="edit-event-title-error"
                class="form-error"
                aria-live="polite"
              ></p>
            </div>

            <div class="form-group">
              <label for="edit-event-description">
                Description
              </label>

              <textarea
                id="edit-event-description"
                name="description"
                rows="5"
              >${escapeHtml(event.description || "")}</textarea>

              <p
                id="edit-event-description-error"
                class="form-error"
                aria-live="polite"
              ></p>
            </div>

            <div class="event-form__row">
              <div class="form-group">
                <label for="edit-event-date">
                  Event Date
                </label>

                <input
                  type="date"
                  id="edit-event-date"
                  name="event_date"
                  value="${escapeHtml(event.event_date)}"
                  required
                />

                <p
                  id="edit-event-date-error"
                  class="form-error"
                  aria-live="polite"
                ></p>
              </div>

              <div class="form-group">
                <label for="edit-event-time">
                  Event Time
                </label>

                <input
                  type="time"
                  id="edit-event-time"
                  name="event_time"
                  value="${escapeHtml(event.event_time)}"
                  required
                />

                <p
                  id="edit-event-time-error"
                  class="form-error"
                  aria-live="polite"
                ></p>
              </div>
            </div>

            <div class="form-group">
              <label for="edit-event-location">
                Location
              </label>

              <input
                type="text"
                id="edit-event-location"
                name="location"
                value="${escapeHtml(event.location)}"
                required
              />

              <p
                id="edit-event-location-error"
                class="form-error"
                aria-live="polite"
              ></p>
            </div>

            <div class="form-group">
              <label for="edit-event-capacity">
                Capacity
              </label>

              <input
                type="number"
                id="edit-event-capacity"
                name="capacity"
                value="${escapeHtml(event.capacity)}"
                min="1"
                step="1"
                required
              />

              <p
                id="edit-event-capacity-error"
                class="form-error"
                aria-live="polite"
              ></p>
            </div>

            <div class="event-form__actions">
              <a
                href="#/event/${numericEventId}"
                class="button button--secondary"
              >
                Cancel
              </a>

              <button type="submit" class="button">
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </section>
    `;

    initializeEditEventForm(
      numericEventId,
      event.status
    );
  } catch (error) {
    console.error("Failed to load event editor.", error);

    renderEditError(
      mainContent,
      error.message || "The event could not be loaded."
    );
  }
}

function initializeEditEventForm(
  eventId,
  originalStatus
) {
  const form = document.getElementById(
    "edit-event-form"
  );

  const titleInput = document.getElementById(
    "edit-event-title"
  );
  const descriptionInput = document.getElementById(
    "edit-event-description"
  );
  const dateInput = document.getElementById(
    "edit-event-date"
  );
  const timeInput = document.getElementById(
    "edit-event-time"
  );
  const locationInput = document.getElementById(
    "edit-event-location"
  );
  const capacityInput = document.getElementById(
    "edit-event-capacity"
  );

  const titleError = document.getElementById(
    "edit-event-title-error"
  );
  const dateError = document.getElementById(
    "edit-event-date-error"
  );
  const timeError = document.getElementById(
    "edit-event-time-error"
  );
  const locationError = document.getElementById(
    "edit-event-location-error"
  );
  const capacityError = document.getElementById(
    "edit-event-capacity-error"
  );

  if (
    !form ||
    !titleInput ||
    !descriptionInput ||
    !dateInput ||
    !timeInput ||
    !locationInput ||
    !capacityInput ||
    !titleError ||
    !dateError ||
    !timeError ||
    !locationError ||
    !capacityError
  ) {
    return;
  }

  const today = new Date();
  const localToday = new Date(
    today.getTime() -
      today.getTimezoneOffset() * 60000
  )
    .toISOString()
    .split("T")[0];

  dateInput.min = localToday;

  form.addEventListener("submit", async (submitEvent) => {
    submitEvent.preventDefault();

    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const eventDate = dateInput.value;
    const eventTime = timeInput.value;
    const location = locationInput.value.trim();
    const capacityValue = capacityInput.value.trim();
    const capacity = Number(capacityValue);

    titleError.textContent = "";
    dateError.textContent = "";
    timeError.textContent = "";
    locationError.textContent = "";
    capacityError.textContent = "";

    let isValid = true;

    if (!title) {
      titleError.textContent =
        "Please enter an event title.";
      isValid = false;
    }

    if (!eventDate) {
      dateError.textContent =
        "Please select an event date.";
      isValid = false;
    } else if (eventDate < localToday) {
      dateError.textContent =
        "Event date cannot be before today.";
      isValid = false;
    }

    if (!eventTime) {
      timeError.textContent =
        "Please select an event time.";
      isValid = false;
    }

    if (!location) {
      locationError.textContent =
        "Please enter an event location.";
      isValid = false;
    }

    if (!capacityValue) {
      capacityError.textContent =
        "Please enter the event capacity.";
      isValid = false;
    } else if (
      !Number.isInteger(capacity) ||
      capacity <= 0
    ) {
      capacityError.textContent =
        "Capacity must be a positive whole number.";
      isValid = false;
    }

    if (!isValid) {
      return;
    }

    const submitButton = form.querySelector(
      'button[type="submit"]'
    );

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Saving...";
    }

    try {
      const response = await authenticatedFetch(
        `http://127.0.0.1:5000/api/events/${eventId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title,
            description,
            event_date: eventDate,
            event_time: eventTime,
            location,
            capacity,
            status:
              originalStatus === "Canceled"
                ? "Canceled"
                : "Updated",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Failed to update event."
        );
      }

      alert("Event updated successfully!");
      window.location.hash = `#/event/${eventId}`;
    } catch (error) {
      console.error("Failed to update event.", error);
      alert(error.message);

      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = "Save Changes";
      }
    }
  });
}