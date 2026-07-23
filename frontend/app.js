import { renderNavbar, initializeNavbar } from "./components/navbar.js";
import { renderFooter } from "./components/footer.js";
import { renderEventsPage } from "./pages/events.js";
import { renderEventDetails } from "./pages/eventDetails.js";


const app = document.getElementById("app");

function renderCurrentPage(mainContent) {
  const hash = window.location.hash;

  if (hash.startsWith("#event/")) {
    const eventId = hash.split("/")[1];
    renderEventDetails(mainContent, eventId);
  } else {
    renderEventsPage(mainContent);
  }
}

function initializeApp() {
  if (!app) {
    console.error("The application container was not found.");
    return;
  }

  // Builds the shared layout with the navbar, main content area & footer
  app.innerHTML = `
    ${renderNavbar()}

    <main id="main-content" class="main-content" tabindex="-1"></main>

    ${renderFooter()}
  `;

  initializeNavbar();
  
  const mainContent = document.getElementById("main-content");
  renderCurrentPage(mainContent);
}

document.addEventListener("DOMContentLoaded", initializeApp);

window.addEventListener("hashchange", () => {
  const mainContent = document.getElementById("main-content");

  if (mainContent) {
    renderCurrentPage(mainContent);
    mainContent.focus();
  }
});