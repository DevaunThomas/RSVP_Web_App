import { API_BASE_URL } from "../config.js";

import {
  getAuthToken,
  logout,
} from "./session.js";

export function buildApiUrl(endpoint = "") {
  if (/^https?:\/\//i.test(endpoint)) {
    return endpoint;
  }

  const normalizedEndpoint = endpoint.startsWith("/")
    ? endpoint
    : `/${endpoint}`;

  return `${API_BASE_URL}${normalizedEndpoint}`;
}

export async function getApiErrorMessage(
  response,
  fallbackMessage = "The request could not be completed."
) {
  try {
    const data = await response.clone().json();

    return (
      data.error ||
      data.message ||
      fallbackMessage
    );
  } catch {
    return fallbackMessage;
  }
}

export async function apiFetch(
  endpoint,
  options = {}
) {
  let response;

  try {
    response = await fetch(
      buildApiUrl(endpoint),
      options
    );
  } catch (error) {
    console.error("API connection failed.", error);

    throw new Error(
      "Unable to connect to the server. Please check your connection and try again."
    );
  }

  if (response.status === 429) {
    const message = await getApiErrorMessage(
      response,
      "Too many requests were made. Please wait and try again."
    );

    throw new Error(message);
  }

  if (response.status >= 500) {
    const message = await getApiErrorMessage(
      response,
      "The server encountered an error. Please try again later."
    );

    throw new Error(message);
  }

  return response;
}

export async function authenticatedFetch(
  endpoint,
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

  const response = await apiFetch(endpoint, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    logout();

    throw new Error(
      "Your session has expired. Please sign in again."
    );
  }

  if (response.status === 403) {
    const message = await getApiErrorMessage(
      response,
      "You do not have permission to perform this action."
    );

    throw new Error(message);
  }

  return response;
}