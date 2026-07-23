export function renderLogin(mainContent) {
  mainContent.innerHTML = `
    <section class="auth-page">
      <div class="auth-card">
        <div class="auth-brand-banner">
          <div class="auth-brand">
            <h1>Campus Events</h1>
            <p>Plan, discover, and RSVP for campus events.</p>
          </div>
        </div>

        <div class="auth-header">
          <h2>Sign In</h2>
          <p>Welcome back! Please enter your credentials.</p>
        </div>

        <form id="login-form" class="auth-form" novalidate>
          <div class="form-group">
            <label for="login-email">Email Address</label>
            <input
              type="email"
              id="login-email"
              name="email"
              placeholder="Enter your email"
              autocomplete="email"
              required
            />
            <p
              id="email-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="form-group">
            <label for="login-password">Password</label>

            <div class="password-field">
              <input
                type="password"
                id="login-password"
                name="password"
                placeholder="Enter your password"
                autocomplete="current-password"
                required
              />

              <button
                type="button"
                id="toggle-password"
                class="password-toggle"
                aria-label="Show password"
              >
                Show
              </button>
            </div>

            <p
              id="password-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <button type="submit" class="button auth-submit">
            Log In
          </button>
        </form>

        <p class="auth-footer-text">
          Don’t have an account?
          <a href="#/register">Create an account</a>
        </p>
      </div>
    </section>
  `;

  initializeLoginForm();
}

function initializeLoginForm() {
  const form = document.getElementById("login-form");
  const emailInput = document.getElementById("login-email");
  const passwordInput = document.getElementById("login-password");
  const emailError = document.getElementById("email-error");
  const passwordError = document.getElementById("password-error");
  const togglePassword = document.getElementById("toggle-password");

  if (
    !form ||
    !emailInput ||
    !passwordInput ||
    !emailError ||
    !passwordError ||
    !togglePassword
  ) {
    return;
  }
  
  if (window.location.search) {
    window.history.replaceState(
        null,
        "",
        `${window.location.pathname}#/login`
    );
}

  togglePassword.addEventListener("click", () => {
    const passwordIsHidden = passwordInput.type === "password";

    passwordInput.type = passwordIsHidden ? "text" : "password";
    togglePassword.textContent = passwordIsHidden ? "Hide" : "Show";
    togglePassword.setAttribute(
      "aria-label",
      passwordIsHidden ? "Hide password" : "Show password"
    );
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    emailError.textContent = "";
    passwordError.textContent = "";

    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    let formIsValid = true;

    if (!email) {
      emailError.textContent = "Please enter your email address.";
      formIsValid = false;
    } else if (!emailInput.validity.valid) {
      emailError.textContent = "Please enter a valid email address.";
      formIsValid = false;
    }

    if (!password) {
      passwordError.textContent = "Please enter your password.";
      formIsValid = false;
    }

    if (!formIsValid) {
      return;
    }

    console.log("Login form is ready for backend integration.", {
      email,
      password,
    });
  });
}