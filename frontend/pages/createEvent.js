import { getCurrentUser } from "../utils/session.js";
import { authenticatedFetch } from "../utils/api.js";

// Render the create event page
export function renderCreateEvent(mainContent) {

  const currentUser = getCurrentUser();

  if (!currentUser) {
    window.location.hash = "#/login";
    return;
  }

  if (currentUser.role !== "organizer") {
    window.location.hash = "#/student-dashboard";
    return;
  }

  mainContent.innerHTML = `
    <section class="form-page">
      <div class="form-page__header">
        <h1>Create Event</h1>
        <p>Add a new campus event for students to discover.</p>
      </div>

      <div class="form-card">
        <form id="create-event-form" class="event-form" novalidate>
          <div class="form-group">
            <label for="event-title">Event Title</label>

            <input
              type="text"
              id="event-title"
              name="title"
              placeholder="Enter the event title"
              required
            />

            <p
              id="event-title-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="form-group">
            <label for="event-description">Description</label>

            <textarea
              id="event-description"
              name="description"
              rows="5"
              placeholder="Describe the event"
            ></textarea>

            <p
              id="event-description-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="event-form__row">
            <div class="form-group">
              <label for="event-date">Event Date</label>

              <input
                type="date"
                id="event-date"
                name="event_date"
                required
              />

              <p
                id="event-date-error"
                class="form-error"
                aria-live="polite"
              ></p>
            </div>

            <div class="form-group">
              <label for="event-time">Event Time</label>

              <input
                type="time"
                id="event-time"
                name="event_time"
                required
              />

              <p
                id="event-time-error"
                class="form-error"
                aria-live="polite"
              ></p>
            </div>
          </div>

          <div class="form-group">
            <label for="event-location">Location</label>

            <input
              type="text"
              id="event-location"
              name="location"
              placeholder="Enter the event location"
              required
            />

            <p
              id="event-location-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="form-group">
            <label for="event-capacity">Capacity</label>

            <input
              type="number"
              id="event-capacity"
              name="capacity"
              placeholder="Enter the maximum number of attendees"
              min="1"
              step="1"
              required
            />

            <p
              id="event-capacity-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="event-form__actions">
            <a
              href="#/organizer-dashboard"
              class="button button--secondary"
            >
              Cancel
            </a>

            <button type="submit" class="button">
              Create Event
            </button>
          </div>
        </form>
      </div>
    </section>
  `;

  initializeCreateEventForm(currentUser);
}

function initializeCreateEventForm(currentUser) {
  const form = document.getElementById("create-event-form");

  const titleInput = document.getElementById("event-title");
  const descriptionInput = document.getElementById("event-description");
  const dateInput = document.getElementById("event-date");
  const timeInput = document.getElementById("event-time");
  const locationInput = document.getElementById("event-location");
  const capacityInput = document.getElementById("event-capacity");

  const titleError = document.getElementById("event-title-error");
  const descriptionError = document.getElementById(
    "event-description-error"
  );
  const dateError = document.getElementById("event-date-error");
  const timeError = document.getElementById("event-time-error");
  const locationError = document.getElementById(
    "event-location-error"
  );
  const capacityError = document.getElementById(
    "event-capacity-error"
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
    !descriptionError ||
    !dateError ||
    !timeError ||
    !locationError ||
    !capacityError
  ) {
    return;
  }

  // Prevent users from selecting a date before today.
  const today = new Date();
  const localToday = new Date(
    today.getTime() - today.getTimezoneOffset() * 60000
  )
    .toISOString()
    .split("T")[0];

  dateInput.min = localToday;

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const eventDate = dateInput.value;
    const eventTime = timeInput.value;
    const location = locationInput.value.trim();
    const capacityValue = capacityInput.value.trim();
    const capacity = Number(capacityValue);

    titleError.textContent = "";
    descriptionError.textContent = "";
    dateError.textContent = "";
    timeError.textContent = "";
    locationError.textContent = "";
    capacityError.textContent = "";

    let isValid = true;

    if (!title) {
      titleError.textContent = "Please enter an event title.";
      isValid = false;
    }

    if (!eventDate) {
      dateError.textContent = "Please select an event date.";
      isValid = false;
    } else if (eventDate < localToday) {
      dateError.textContent =
        "Event date cannot be before today.";
      isValid = false;
    }

    if (!eventTime) {
      timeError.textContent = "Please select an event time.";
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
    } else if (!Number.isInteger(capacity) || capacity <= 0) {
      capacityError.textContent =
        "Capacity must be a positive whole number.";
      isValid = false;
    }

    if (!isValid) {
      return;
    }

    const eventData = {
        title,
        description,
        event_date: eventDate,
        event_time: eventTime,
        location,
        capacity,
        organizer_id: currentUser.user_id
        };
        
        authenticatedFetch("http://127.0.0.1:5000/api/events", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            
            body: JSON.stringify(eventData),
        })
        
        .then(async (response) => {
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || "Failed to create event.");
            }
            
            alert("Event created successfully!");
            
            window.location.hash = "#/organizer-dashboard";
        })
        .catch((error) => {
            alert(error.message);
            console.error(error);
        });
    });
}