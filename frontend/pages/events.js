import {
  renderEventCard }
  from "../components/eventCard.js";

import {
  resolveEventStatus
} from "../utils/eventStatus.js";

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

function filterEvents(events, searchQuery, selectedDate) {
  const normalizedQuery = searchQuery.trim().toLowerCase();

  return events.filter((event) => {
    const searchableText = [
      event.title,
      event.description,
      event.location,
      event.organizer,
    ]
      .join(" ")
      .toLowerCase();

    const matchesSearch =
      normalizedQuery === "" || searchableText.includes(normalizedQuery);

    const matchesDate =
      selectedDate === "" || event.date === selectedDate;

    return matchesSearch && matchesDate;
  });
}

function renderEmptyState(hasActiveFilters) {
  if (hasActiveFilters) {
    return `
      <div class="empty-state" role="status">
        <h2>No matching events</h2>
        <p>Try changing your search term or selected date.</p>

        <button
          class="button button--secondary"
          id="clear-event-filters"
          type="button"
        >
          Clear Filters
        </button>
      </div>
    `;
  }

  return `
    <div class="empty-state" role="status">
      <h2>No upcoming events</h2>
      <p>New campus events will appear here when they are available.</p>
    </div>
  `;
}

function renderErrorState() {
  return `
    <div class="error-state" role="alert">
      <h2>Events could not be loaded</h2>
      <p>Please refresh the page and try again.</p>
    </div>
  `;
}

export async function renderEventsPage(container) {
  if (!container) {
    console.error("The Events page container was not found.");
    return;
  }

  container.innerHTML = `
    <section class="page-loading" role="status" aria-live="polite">
      <p>Loading upcoming events…</p>
    </section>
  `;

  try {
    const response = await fetch(
      "http://127.0.0.1:5000/api/events"
    );

    if (!response.ok) {
      throw new Error("Failed to load events.");
    }

    const apiEvents = await response.json();

    if (!Array.isArray(apiEvents)) {
      throw new Error("Event data must be an array.");
    }

    const events = apiEvents.map((event) => ({
      id: event.event_id,
      title: event.title,
      description: event.description || "",
      date: event.event_date,
      startTime: event.event_time,
      endTime: event.end_time || null,
      location: event.location,
      organizer: event.organizer_name || "Unknown organizer",
      capacity: Number(event.capacity) || 0,
      rsvpCount: Number(event.registered_count) || 0,
       status:
        event.status?.toLowerCase() === "active"
          ? "open"
          : event.status?.toLowerCase() || "open",
    }));
    
    const upcomingEvents = events
  .map((event) => ({
    ...event,
    status: resolveEventStatus(event),
  }))
  .filter((event) => event.status !== "past");

const sortedEvents = sortEventsByDate(upcomingEvents);

  
    
    container.innerHTML = `
      <section class="events-hero">
        <div class="events-hero__content">

          <h1>
          Upcoming Campus Events
          </h1>

          <p class="events-hero__description">
            Discover activities, workshops, and student events happening
            across campus.
          </p>
        </div>
      </section>

      <section class="events-section" aria-labelledby="events-section-title">
        <div class="events-section__header">
          <div>
            <h2 id="events-section-title">Explore Events</h2>

            <p
              class="events-results-count"
              id="events-results-count"
              aria-live="polite"
            ></p>
          </div>
        </div>

        <form class="event-filters" id="event-filters">
          <div class="form-field">
            <label for="event-search">Search events</label>

            <input
              id="event-search"
              name="search"
              type="search"
              placeholder="Search by event, location, or organizer"
              autocomplete="off"
            />
          </div>

          <div class="form-field">
            <label for="event-date-filter">Filter by date</label>

            <input
              id="event-date-filter"
              name="date"
              type="date"
            />
          </div>
        </form>

        <div
          class="event-grid"
          id="event-grid"
          aria-live="polite"
        ></div>
      </section>
    `;

    const filtersForm = container.querySelector("#event-filters");
    const searchInput = container.querySelector("#event-search");
    const dateInput = container.querySelector("#event-date-filter");
    const eventGrid = container.querySelector("#event-grid");
    const resultsCount = container.querySelector("#events-results-count");

    function updateEvents() {
      const searchQuery = searchInput.value;
      const selectedDate = dateInput.value;

      const filteredEvents = filterEvents(
        sortedEvents,
        searchQuery,
        selectedDate
      );

      const hasActiveFilters =
        searchQuery.trim() !== "" || selectedDate !== "";

      resultsCount.textContent = `${filteredEvents.length} ${
        filteredEvents.length === 1 ? "event" : "events"
      } found`;

      eventGrid.innerHTML =
        filteredEvents.length > 0
          ? filteredEvents.map(renderEventCard).join("")
          : renderEmptyState(hasActiveFilters);
    }

    // Prevents the filter form from reloading the page
    filtersForm.addEventListener("submit", (event) => {
      event.preventDefault();
      updateEvents();
    });
    
    searchInput.addEventListener("input", updateEvents);
    dateInput.addEventListener("change", updateEvents);

    eventGrid.addEventListener("click", (event) => {
      const clearButton = event.target.closest("#clear-event-filters");

      if (!clearButton) {
        return;
      }

      searchInput.value = "";
      dateInput.value = "";
      updateEvents();
      searchInput.focus();
    });

    updateEvents();
  } catch (error) {
    console.error("Failed to render the Events page.", error);
    container.innerHTML = renderErrorState();
  }
}