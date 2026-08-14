const CURRENT_USER_KEY = "currentUser";
const AUTH_TOKEN_KEY = "authToken";

export function getCurrentUser() {
  const user = localStorage.getItem(CURRENT_USER_KEY);

  return user ? JSON.parse(user) : null;
}

export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function saveSession(user, token) {
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