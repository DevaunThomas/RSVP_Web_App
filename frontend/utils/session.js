export function getCurrentUser() {
  const user = localStorage.getItem("currentUser");

  return user ? JSON.parse(user) : null;
}

export function logout() {
  localStorage.removeItem("currentUser");

  window.location.hash = "#/login";
  window.location.reload();
}