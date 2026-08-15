const LOCAL_API_BASE_URL =
  "http://127.0.0.1:5000/api";

const configuredApiBaseUrl =
  globalThis.APP_CONFIG?.API_BASE_URL;

const defaultApiBaseUrl = [
  "localhost",
  "127.0.0.1",
].includes(globalThis.location.hostname)
  ? LOCAL_API_BASE_URL
  : `${globalThis.location.origin}/api`;

export const API_BASE_URL = (
  configuredApiBaseUrl || defaultApiBaseUrl
).replace(/\/+$/, "");