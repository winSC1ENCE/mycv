import { http } from "./client";
import type { User } from "./types";

export async function login(username: string, password: string): Promise<User> {
  const { data } = await http.post<User>("/auth/login/", { username, password });
  return data;
}

export async function logout(): Promise<void> {
  await http.post("/auth/logout/");
}

export async function fetchMe(): Promise<User> {
  const { data } = await http.get<User>("/auth/me/");
  return data;
}
