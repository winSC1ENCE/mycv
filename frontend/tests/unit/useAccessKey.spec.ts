import { describe, expect, it, vi, beforeEach } from "vitest";
import { createPinia, setActivePinia } from "pinia";

// Mock vue-router before any imports that use it
const replaceMock = vi.fn();
const isReadyMock = vi.fn(() => Promise.resolve());
vi.mock("vue-router", () => ({
  useRouter: () => ({ replace: replaceMock, isReady: isReadyMock }),
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

function setLocationSearch(search: string): void {
  // jsdom exposes window.location.search as writable via Object.defineProperty
  Object.defineProperty(window, "location", {
    writable: true,
    value: { ...window.location, search },
  });
}

describe("useAccessKey", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    replaceMock.mockReset();
    loadMock.mockReset();
    isReadyMock.mockClear();
    setLocationSearch("");
  });

  it("stores the key and reloads cv when ?key is present", async () => {
    setLocationSearch("?key=TOKEN_ABC");
    useAccessKey();
    expect(localStorage.getItem("mycv:access_key")).toBe("TOKEN_ABC");
    expect(loadMock).toHaveBeenCalledOnce();
    await isReadyMock.mock.results[0]?.value;
    expect(replaceMock).toHaveBeenCalledWith({ query: {} });
  });

  it("strips the key from the URL but preserves other query params", async () => {
    setLocationSearch("?key=XYZ&foo=bar");
    useAccessKey();
    await isReadyMock.mock.results[0]?.value;
    expect(replaceMock).toHaveBeenCalledWith({ query: { foo: "bar" } });
  });

  it("does nothing when there is no key in the query", () => {
    setLocationSearch("");
    useAccessKey();
    expect(loadMock).not.toHaveBeenCalled();
    expect(replaceMock).not.toHaveBeenCalled();
    expect(localStorage.getItem("mycv:access_key")).toBeNull();
  });

  it("does nothing when key is an empty string", () => {
    setLocationSearch("?key=");
    useAccessKey();
    expect(loadMock).not.toHaveBeenCalled();
  });
});
