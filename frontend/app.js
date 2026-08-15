import {
  renderNavbar,
  initializeNavbar,
  updateNavbarActiveState,
} from "./components/navbar.js";

import {
  renderFooter,
} from "./components/footer.js";

import {
  renderEventsPage,
} from "./pages/events.js";

import {
  renderEventDetails,
} from "./pages/eventDetails.js";

import { renderLogin } from "./pages/login.js";
import { renderRegister } from "./pages/register.js";

import {
  renderStudentDashboard,
} from "./pages/studentDashboard.js";

import {
  renderOrganizerDashboard,
} from "./pages/organizerDashboard.js";

import {
  renderCreateEvent,
} from "./pages/createEvent.js";

import {
  renderEditEvent,
} from "./pages/editEvent.js";

import {
  renderManageAttendees,
} from "./pages/manageAttendees.js";

import {
  renderNotifications,
} from "./pages/notifications.js";

const app = document.getElementById("app");

function renderCurrentPage(mainContent) {
  const hash = window.location.hash;

  updateNavbarActiveState();

  if (hash === "#/login" || hash === "#login") {
    renderLogin(mainContent);
    return;
  }

  if (hash === "#/register" || hash === "#register") {
    renderRegister(mainContent);
    return;
  }

  if (
    hash === "#/notifications" ||
    hash === "#notifications"
  ) {
    renderNotifications(mainContent);
    return;
  }

  if (
    hash === "#/student-dashboard" ||
    hash === "#student-dashboard"
  ) {
    renderStudentDashboard(mainContent);
    return;
  }

  if (
    hash === "#/organizer-dashboard" ||
    hash === "#organizer-dashboard"
  ) {
    renderOrganizerDashboard(mainContent);
    return;
  }

  if (hash === "#/create-event" || hash === "#create-event") {
    renderCreateEvent(mainContent);
    return;
  }
  if (
    hash.startsWith("#/edit-event/") ||
    hash.startsWith("#edit-event/")
  ) {
    const eventId = hash.split("/").pop();

    renderEditEvent(mainContent, eventId);
    return;
  }

  if (
    hash.startsWith("#/manage-attendees/") ||
    hash.startsWith("#manage-attendees/")
  ) {
    const eventId = hash.split("/").pop();

    renderManageAttendees(mainContent, eventId);
    return;
  }
  
  if (hash.startsWith("#/event/") || hash.startsWith("#event/")) {
    const eventId = hash.split("/").pop();
    
    renderEventDetails(mainContent, eventId);
    return;
  }

  renderEventsPage(mainContent);
}

function initializeApp() {
  if (!app) {
    console.error("The application container was not found.");
    return;
  }

  // Builds the shared layout with the navbar, main content area, and footer
  app.innerHTML = `
    ${renderNavbar()}

    <main id="main-content" class="main-content" tabindex="-1"></main>

    ${renderFooter()}
  `;

  initializeNavbar();

  const mainContent = document.getElementById("main-content");

  if (mainContent) {
    renderCurrentPage(mainContent);
  }
}

document.addEventListener("DOMContentLoaded", initializeApp);

window.addEventListener("hashchange", () => {
  const mainContent = document.getElementById("main-content");

  if (mainContent) {
    renderCurrentPage(mainContent);
    mainContent.focus();
  }
});