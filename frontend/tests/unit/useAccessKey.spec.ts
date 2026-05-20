import { describe, expect, it, vi, beforeEach } from "vitest";
import { createPinia, setActivePinia } from "pinia";

// Mock vue-router before any imports that use it
const replaceMock = vi.fn();
vi.mock("vue-router", () => ({
  useRoute: () => ({ query: routeQuery }),
  useRouter: () => ({ replace: replaceMock }),
}));

// Mock the cv store
const loadMock = vi.fn();
vi.mock("@/stores/cv", () => ({
  useCvStore: () => ({ load: loadMock }),
}));

// Mock localStorage via the client module
vi.mock("@/api/client", () => ({
  storeAccessKey: vi.fn((key: string) => localStorage.setItem("mycv:access_key", key)),
  getStoredAccessKey: vi.fn(() => localStorage.getItem("mycv:access_key")),
}));

import { useAccessKey } from "@/composables/useAccessKey";

let routeQuery: Record<string, string> = {};

describe("useAccessKey", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    replaceMock.mockReset();
    loadMock.mockReset();
    routeQuery = {};
  });

  it("stores the key and reloads cv when ?key is present", () => {
    routeQuery = { key: "TOKEN_ABC" };
    useAccessKey();
    expect(localStorage.getItem("mycv:access_key")).toBe("TOKEN_ABC");
    expect(loadMock).toHaveBeenCalledOnce();
    expect(replaceMock).toHaveBeenCalledWith({ query: {} });
  });

  it("strips the key from the URL but preserves other query params", () => {
    routeQuery = { key: "XYZ", foo: "bar" };
    useAccessKey();
    expect(replaceMock).toHaveBeenCalledWith({ query: { foo: "bar" } });
  });

  it("does nothing when there is no key in the query", () => {
    routeQuery = {};
    useAccessKey();
    expect(loadMock).not.toHaveBeenCalled();
    expect(replaceMock).not.toHaveBeenCalled();
    expect(localStorage.getItem("mycv:access_key")).toBeNull();
  });

  it("does nothing when key is an empty string", () => {
    routeQuery = { key: "" };
    useAccessKey();
    expect(loadMock).not.toHaveBeenCalled();
  });
});
