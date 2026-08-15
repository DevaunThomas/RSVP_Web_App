import {
  getCurrentUser,
  logout,
} from "../utils/session.js";

import {
  authenticatedFetch,
} from "../utils/api.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


export function renderNavbar() {
  const currentUser = getCurrentUser();

  const dashboardRoute =
    currentUser?.role === "organizer"
      ? "#/organizer-dashboard"
      : "#/student-dashboard";

  const dashboardLabel = "Dashboard";

  const authButtons = currentUser
    ? `
      <a
        class="navbar__link navbar__notifications-link"
        href="#/notifications"
        data-nav-route="notifications"
        aria-label="Notifications"
      >
        Notifications

        <span
          id="notification-count-badge"
          class="navbar__notification-badge"
          hidden
        ></span>
      </a>
      <a
        class="navbar__link"
        href="${dashboardRoute}"
        data-nav-route="dashboard"
      >
        ${dashboardLabel}
      </a>

      <div class="navbar__user" aria-label="Signed in user">
        <span class="navbar__user-name">
          ${escapeHtml(currentUser.name)}
        </span>

        <span class="navbar__user-role">
          ${escapeHtml(currentUser.role)}
        </span>
      </div>

      <button
        id="logout-button"
        class="button button--secondary navbar__logout"
        type="button"
      >
        Log Out
      </button>
    `
    : `
      <a class="button button--secondary" href="#/login">
        Log In
      </a>

      <a class="button button--primary" href="#/register">
        Register
      </a>
    `;

  return `
    <header class="site-header">
      <nav class="navbar" aria-label="Main navigation">
        <a
          class="navbar__brand"
          href="#/events"
          aria-label="UM-Dearborn Campus Events home"
        >
          <img
            class="navbar__logo"
            src="./assets/um-dearborn-logo.webp"
            alt=""
            width="104"
            height="96"
          />
        </a>

        <button
          class="navbar__toggle"
          type="button"
          aria-expanded="false"
          aria-controls="navbar-menu"
          aria-label="Open navigation menu"
        >
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </button>

        <div class="navbar__menu" id="navbar-menu">
          <a
            class="navbar__link"
            href="#/events"
            data-nav-route="events"
          >
            Events
          </a>

          <div class="navbar__actions">
            ${authButtons}
          </div>
        </div>
      </nav>
    </header>
  `;
}

export async function updateNotificationBadge() {
  const currentUser = getCurrentUser();

  const badge = document.getElementById(
    "notification-count-badge"
  );

  const notificationLink = document.querySelector(
    ".navbar__notifications-link"
  );

  if (!currentUser || !badge || !notificationLink) {
    return;
  }

  try {
    const response = await authenticatedFetch(
      `/users/${currentUser.user_id}/notifications/unread-count`
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error ||
          "Unable to load the notification count."
      );
    }

    const unreadCount =
      Number(data.unread_count) || 0;

    badge.textContent =
      unreadCount > 99 ? "99+" : String(unreadCount);

    badge.hidden = unreadCount === 0;

    notificationLink.setAttribute(
      "aria-label",
      unreadCount === 0
        ? "Notifications"
        : `Notifications, ${unreadCount} unread`
    );
  } catch (error) {
    console.error(
      "Unable to update notification count.",
      error
    );

    badge.hidden = true;
  }
}

export function updateNavbarActiveState() {

  const route = window.location.hash
    .replace(/^#\/?/, "")
    .toLowerCase();

  const isNotificationsRoute =
    route === "notifications";

  const dashboardRoutes = [
    "student-dashboard",
    "organizer-dashboard",
    "create-event",
  ];

  const isDashboardRoute =
    dashboardRoutes.includes(route) ||
    route.startsWith("edit-event/") ||
    route.startsWith("manage-attendees/");

  const isEventsRoute =
    route === "" ||
    route === "events" ||
    route.startsWith("event/");

  let activeRoute = null;

  if (isDashboardRoute) {
    activeRoute = "dashboard";
  } else if (isNotificationsRoute) {
    activeRoute = "notifications";
  } else if (isEventsRoute) {
    activeRoute = "events";
  }

  const navigationLinks = document.querySelectorAll(
    "[data-nav-route]"
  );

  navigationLinks.forEach((link) => {
    const isActive =
      link.dataset.navRoute === activeRoute;

    link.classList.toggle(
      "navbar__link--active",
      isActive
    );

    if (isActive) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
}

export function initializeNavbar() {
  const toggleButton = document.querySelector(".navbar__toggle");
  const navigationMenu = document.querySelector(".navbar__menu");
  const logoutButton = document.getElementById("logout-button");

  if (logoutButton) {
    logoutButton.addEventListener("click", logout);
  }
    updateNotificationBadge();

  if (!toggleButton || !navigationMenu) {
    return;
  }

  function closeMenu() {
    toggleButton.setAttribute("aria-expanded", "false");
    toggleButton.setAttribute(
      "aria-label",
      "Open navigation menu"
    );
    navigationMenu.classList.remove("navbar__menu--open");
  }

  toggleButton.addEventListener("click", () => {
    const isOpen =
      toggleButton.getAttribute("aria-expanded") === "true";

    toggleButton.setAttribute(
      "aria-expanded",
      String(!isOpen)
    );

    toggleButton.setAttribute(
      "aria-label",
      isOpen
        ? "Open navigation menu"
        : "Close navigation menu"
    );

    navigationMenu.classList.toggle(
      "navbar__menu--open",
      !isOpen
    );
  });

  navigationMenu.addEventListener("click", (event) => {
    if (
      event.target.closest("a") ||
      event.target.closest("button")
    ) {
      closeMenu();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 768) {
      closeMenu();
    }
  });
}