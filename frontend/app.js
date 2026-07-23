import { renderNavbar, initializeNavbar } from "./components/navbar.js";
import { renderFooter } from "./components/footer.js";
import { renderEventsPage } from "./pages/events.js";
import { renderEventDetails } from "./pages/eventDetails.js";
import { renderLogin } from "./pages/login.js";

const app = document.getElementById("app");

function renderCurrentPage(mainContent) {
  const hash = window.location.hash;

  if (hash === "#/login") {
    renderLogin(mainContent);
    return;
  }

  if (hash.startsWith("#event/")) {
    const eventId = hash.split("/")[1];
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