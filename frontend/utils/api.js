import {
  getAuthToken,
  logout,
} from "./session.js";

export async function authenticatedFetch(
  url,
  options = {}
) {
  const token = getAuthToken();

  if (!token) {
    logout();
    throw new Error(
      "Your session has ended. Please sign in again."
    );
  }

  const headers = new Headers(options.headers || {});

  headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    logout();
    throw new Error(
      "Your session has expired. Please sign in again."
    );
  }

  return response;
}