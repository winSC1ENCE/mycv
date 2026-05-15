import axios from "axios";
import type { Cv } from "./types";

const baseURL = import.meta.env.VITE_API_BASE ?? "/api";

export const http = axios.create({ baseURL, withCredentials: true, timeout: 10_000 });

// Attach CSRF token from cookie on all state-changing requests
http.interceptors.request.use((config) => {
  const method = config.method?.toUpperCase() ?? "";
  if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    if (match) config.headers["X-CSRFToken"] = match[1];
  }
  return config;
});

export async function fetchCv(): Promise<Cv> {
  const { data } = await http.get<Cv>("/cv/");
  return data;
}
