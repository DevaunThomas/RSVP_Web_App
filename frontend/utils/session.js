const CURRENT_USER_KEY = "currentUser";
const AUTH_TOKEN_KEY = "authToken";

function isValidUser(user) {
  const validRoles = [
    "student",
    "organizer",
  ];

  return (
    user &&
    Number.isInteger(Number(user.user_id)) &&
    typeof user.name === "string" &&
    validRoles.includes(user.role)
  );
}

export function getCurrentUser() {
  const storedUser =
    localStorage.getItem(CURRENT_USER_KEY);

  if (!storedUser) {
    return null;
  }

  try {
    const user = JSON.parse(storedUser);

    if (!isValidUser(user)) {
      clearSession();
      return null;
    }

    return user;
  } catch (error) {
    console.error(
      "The stored user session is invalid.",
      error
    );

    clearSession();
    return null;
  }
}

export function getAuthToken() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);

  return token && token.trim()
    ? token
    : null;
}

export function saveSession(user, token) {
  if (
    !isValidUser(user) ||
    typeof token !== "string" ||
    !token.trim()
  ) {
    throw new Error(
      "A valid user and authentication token are required."
    );
  }

  localStorage.setItem(
    CURRENT_USER_KEY,
    JSON.stringify(user)
  );

  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearSession() {
  localStorage.removeItem(CURRENT_USER_KEY);
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export function logout() {
  clearSession();

  window.location.hash = "#/login";
  window.location.reload();
}