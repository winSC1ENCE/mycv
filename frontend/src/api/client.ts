import axios from "axios";
import type { Cv } from "./types";

const baseURL = import.meta.env.VITE_API_BASE ?? "/api";

export const http = axios.create({ baseURL, withCredentials: true, timeout: 10_000 });

export async function fetchCv(): Promise<Cv> {
  const { data } = await http.get<Cv>("/cv/");
  return data;
}
