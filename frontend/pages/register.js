import { apiFetch } from "../utils/api.js";

export function renderRegister(mainContent) {
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
          <h2>Create Account</h2>
          <p>Register as a student or event organizer.</p>
        </div>

        <!-- Registration fields -->
        <form id="register-form" class="auth-form" novalidate>
          <div class="form-group">
            <label for="register-name">Full Name</label>
            <input
              type="text"
              id="register-name"
              name="name"
              placeholder="Enter your full name"
              autocomplete="name"
              required
            />
            <p
              id="name-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="form-group">
            <label for="register-email">Email Address</label>
            <input
              type="email"
              id="register-email"
              name="email"
              placeholder="Enter your email"
              autocomplete="email"
              required
            />
            <p
              id="register-email-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="form-group">
            <label for="register-password">Password</label>

            <div class="password-field">
              <input
                type="password"
                id="register-password"
                name="password"
                placeholder="Create a password"
                autocomplete="new-password"
                required
              />

              <button
                type="button"
                id="toggle-register-password"
                class="password-toggle"
                aria-label="Show password"
              >
                Show
              </button>
            </div>

            <p
              id="register-password-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="form-group">
            <label for="confirm-password">Confirm Password</label>

            <div class="password-field">
              <input
                type="password"
                id="confirm-password"
                name="confirmPassword"
                placeholder="Re-enter your password"
                autocomplete="new-password"
                required
              />

              <button
                type="button"
                id="toggle-confirm-password"
                class="password-toggle"
                aria-label="Show confirmed password"
              >
                Show
              </button>
            </div>

            <p
              id="confirm-password-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <div class="form-group">
            <label for="register-role">Account Type</label>

            <select id="register-role" name="role" required>
              <option value="">Select an account type</option>
              <option value="student">Student</option>
              <option value="organizer">Event Organizer</option>
            </select>

            <p
              id="role-error"
              class="form-error"
              aria-live="polite"
            ></p>
          </div>

          <button type="submit" class="button auth-submit">
            Create Account
          </button>
        </form>

        <!-- Link back to the login page -->
        <p class="auth-footer-text">
          Already have an account?
          <a href="#/login">Sign in</a>
        </p>
      </div>
    </section>
  `;

  initializeRegisterForm();
}

function initializeRegisterForm() {
  const form = document.getElementById("register-form");
  const passwordInput = document.getElementById("register-password");
  const confirmPasswordInput = document.getElementById("confirm-password");
  const passwordToggle = document.getElementById(
    "toggle-register-password"
  );
  const confirmPasswordToggle = document.getElementById(
    "toggle-confirm-password"
  );

  if (
    !form ||
    !passwordInput ||
    !confirmPasswordInput ||
    !passwordToggle ||
    !confirmPasswordToggle
  ) {
    return;
  }

  passwordToggle.addEventListener("click", () => {
    togglePasswordVisibility(passwordInput, passwordToggle);
  });

  confirmPasswordToggle.addEventListener("click", () => {
    togglePasswordVisibility(
      confirmPasswordInput,
      confirmPasswordToggle
    );
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const nameInput = document.getElementById("register-name");
    const emailInput = document.getElementById("register-email");
    const roleInput = document.getElementById("register-role");

    const nameError = document.getElementById("name-error");
    const emailError = document.getElementById(
      "register-email-error"
    );
    const passwordError = document.getElementById(
      "register-password-error"
    );
    const confirmPasswordError = document.getElementById(
      "confirm-password-error"
    );
    const roleError = document.getElementById("role-error");

    if (
      !nameInput ||
      !emailInput ||
      !roleInput ||
      !nameError ||
      !emailError ||
      !passwordError ||
      !confirmPasswordError ||
      !roleError
    ) {
      return;
    }

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    const role = roleInput.value;

    nameError.textContent = "";
    emailError.textContent = "";
    passwordError.textContent = "";
    confirmPasswordError.textContent = "";
    roleError.textContent = "";

    let isValid = true;

    if (!name) {
      nameError.textContent = "Please enter your full name.";
      isValid = false;
    }

    if (!email) {
      emailError.textContent = "Please enter your email address.";
      isValid = false;
    } else if (!emailInput.validity.valid) {
      emailError.textContent =
        "Please enter a valid email address.";
      isValid = false;
    }

    if (!password) {
      passwordError.textContent = "Please create a password.";
      isValid = false;
    } else if (password.length < 8) {
      passwordError.textContent =
        "Password must be at least 8 characters long.";
      isValid = false;
    }

    if (!confirmPassword) {
      confirmPasswordError.textContent =
        "Please confirm your password.";
      isValid = false;
    } else if (password !== confirmPassword) {
      confirmPasswordError.textContent =
        "Passwords do not match.";
      isValid = false;
    }

    if (!role) {
      roleError.textContent =
        "Please select an account type.";
      isValid = false;
    }

    if (!isValid) {
      return;
    }

    const registrationData = {
      name,
      email,
      password,
      role,
    };

    const submitButton = form.querySelector('button[type="submit"]');

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Creating Account...";
    }

    try {
      const response = await apiFetch(
        "/users",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(registrationData),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          emailError.textContent =
            data.error || "An account with this email already exists.";
          return;
        }

        throw new Error(data.error || "Unable to create account.");
      }

      alert("Account created successfully. Please sign in.");
      window.location.hash = "#/login";
    } catch (error) {
      console.error("Registration failed.", error);
      roleError.textContent =
        error.message || "Unable to create account.";
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = "Create Account";
      }
    }
  });
}

function togglePasswordVisibility(input, button) {
  const isHidden = input.type === "password";

  input.type = isHidden ? "text" : "password";
  button.textContent = isHidden ? "Hide" : "Show";
  button.setAttribute(
    "aria-label",
    isHidden ? "Hide password" : "Show password"
  );
}