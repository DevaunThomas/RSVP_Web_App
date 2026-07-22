export function renderNavbar() {
  return `
    <header class="site-header">
      <nav class="navbar" aria-label="Main navigation">
        <a
            class="navbar__brand"
            href="#events"
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

        <!-- Controls the navigation menu on smaller screens -->
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
          <a class="navbar__link navbar__link--active" href="#events">
            Events
          </a>

          <div class="navbar__actions">
            <a class="button button--secondary" href="#login">
              Log in
            </a>

            <a class="button button--primary" href="#register">
              Register
            </a>
          </div>
        </div>
      </nav>
    </header>
  `;
}

export function initializeNavbar() {
  const toggleButton = document.querySelector(".navbar__toggle");
  const navigationMenu = document.querySelector(".navbar__menu");

  if (!toggleButton || !navigationMenu) {
    return;
  }

  function closeMenu() {
    toggleButton.setAttribute("aria-expanded", "false");
    toggleButton.setAttribute("aria-label", "Open navigation menu");
    navigationMenu.classList.remove("navbar__menu--open");
  }

  toggleButton.addEventListener("click", () => {
    const isOpen = toggleButton.getAttribute("aria-expanded") === "true";

    toggleButton.setAttribute("aria-expanded", String(!isOpen));
    toggleButton.setAttribute(
      "aria-label",
      isOpen ? "Open navigation menu" : "Close navigation menu"
    );

    navigationMenu.classList.toggle("navbar__menu--open", !isOpen);
  });

  navigationMenu.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      closeMenu();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 768) {
      closeMenu();
    }
  });
}