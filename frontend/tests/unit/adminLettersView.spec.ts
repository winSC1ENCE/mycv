import { describe, expect, it, vi, beforeEach } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import en from "@/locales/en.json";

function appRow(over: Record<string, unknown> = {}) {
  return {
    id: 5,
    name: "ACME GmbH",
    content: "",
    content_de: "",
    version: "v1.0.0",
    letter_content: "",
    letter_content_de: "",
    letter_reference: "JOB-1",
    access_key: null,
    access_url: "",
    expires_display: "",
    updated_display: "",
    order: 0,
    is_published: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...over,
  };
}

vi.mock("@/api/admin", () => ({
  readmeApi: {
    list: vi.fn(async () => ({ count: 1, next: null, previous: null, results: [appRow()] })),
    update: vi.fn(async (id: number, p: object) => ({ id, name: "ACME GmbH", ...p })),
    pdf: vi.fn(async () => new Blob(["%PDF"], { type: "application/pdf" })),
  },
  accessKeyApi: { list: vi.fn(async () => ({ results: [] })) },
}));

// Controllable route query (deep-link from the Applications section).
const routeMock = vi.hoisted(() => ({ query: {} as Record<string, string> }));
vi.mock("vue-router", () => ({ useRoute: () => ({ query: routeMock.query }) }));

import AdminLettersView from "@/views/admin/AdminLettersView.vue";
import { readmeApi } from "@/api/admin";

const i18n = createI18n({ legacy: false, locale: "en", messages: { en } });

function mountView() {
  return mount(AdminLettersView, { global: { plugins: [i18n] } });
}

function byText(buttons: ReturnType<ReturnType<typeof mountView>["findAll"]>, text: string) {
  return buttons.find((b) => b.text().includes(text));
}

beforeEach(() => {
  vi.clearAllMocks();
  routeMock.query = {};
  global.URL.createObjectURL = vi.fn(() => "blob:x");
  global.URL.revokeObjectURL = vi.fn();
});

describe("AdminLettersView", () => {
  it("lists the same applications with their reference", async () => {
    const wrapper = mountView();
    await flushPromises();
    expect(readmeApi.list).toHaveBeenCalled();
    expect(wrapper.text()).toContain("Motivation Letters");
    expect(wrapper.text()).toContain("ACME GmbH");
    expect(wrapper.text()).toContain("JOB-1");
  });

  it("opens the letter editor under the row and saves letter fields", async () => {
    const wrapper = mountView();
    await flushPromises();
    await wrapper.find(".btn-icon").trigger("click"); // ✏
    await flushPromises();
    const refInput = wrapper.find('input[placeholder="JOB-2026-042"]');
    await refInput.setValue("JOB-9");
    await wrapper.find("form").trigger("submit");
    await flushPromises();
    expect(readmeApi.update).toHaveBeenCalledWith(
      5,
      expect.objectContaining({ letter_reference: "JOB-9" }),
    );
  });

  it("exports the letter PDF with doc=letter", async () => {
    const wrapper = mountView();
    await flushPromises();
    await wrapper.find(".btn-icon").trigger("click");
    await flushPromises();
    await byText(wrapper.findAll("button"), "PDF EN")!.trigger("click");
    await flushPromises();
    expect(readmeApi.pdf).toHaveBeenCalledWith(
      5,
      "en",
      expect.any(Array),
      expect.any(String),
      "letter",
    );
  });

  it("auto-opens the editor when deep-linked via ?edit=<id>", async () => {
    routeMock.query = { edit: "5" };
    const wrapper = mountView();
    await flushPromises();
    // editor row for the matching application is open without a click
    expect(wrapper.find('input[placeholder="JOB-2026-042"]').exists()).toBe(true);
  });
});
