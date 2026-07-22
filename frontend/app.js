import { renderNavbar, initializeNavbar } from "./components/navbar.js";
import { renderFooter } from "./components/footer.js";
import { renderEventsPage } from "./pages/events.js";

const app = document.getElementById("app");

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
  renderEventsPage(mainContent);
}

document.addEventListener("DOMContentLoaded", initializeApp);