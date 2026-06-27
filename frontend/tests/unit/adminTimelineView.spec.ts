import { describe, expect, it, vi, beforeEach } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import en from "@/locales/en.json";

vi.mock("@/api/admin", () => ({
  timelineApi: {
    list: vi.fn(async () => ({ count: 0, next: null, previous: null, results: [] })),
    create: vi.fn(),
    update: vi.fn(),
    destroy: vi.fn(),
    reorder: vi.fn(),
  },
  cvApi: {
    pdf: vi.fn(async () => new Blob(["%PDF"], { type: "application/pdf" })),
  },
}));

import AdminTimelineView from "@/views/admin/AdminTimelineView.vue";
import { cvApi } from "@/api/admin";

const i18n = createI18n({ legacy: false, locale: "en", messages: { en } });

function mountView() {
  return mount(AdminTimelineView, { global: { plugins: [i18n] } });
}

function byText(buttons: ReturnType<ReturnType<typeof mountView>["findAll"]>, text: string) {
  return buttons.find((b) => b.text().includes(text));
}

beforeEach(() => {
  vi.clearAllMocks();
  global.URL.createObjectURL = vi.fn(() => "blob:x");
  global.URL.revokeObjectURL = vi.fn();
});

describe("AdminTimelineView", () => {
  it("exports the CV PDF in English", async () => {
    const wrapper = mountView();
    await flushPromises();
    await byText(wrapper.findAll("button"), "PDF EN")!.trigger("click");
    await flushPromises();
    expect(cvApi.pdf).toHaveBeenCalledWith("en", expect.any(String));
    expect(global.URL.createObjectURL).toHaveBeenCalled();
  });

  it("exports the CV PDF in German", async () => {
    const wrapper = mountView();
    await flushPromises();
    await byText(wrapper.findAll("button"), "PDF DE")!.trigger("click");
    await flushPromises();
    expect(cvApi.pdf).toHaveBeenCalledWith("de", expect.any(String));
  });

  it("surfaces an error when the export fails", async () => {
    vi.mocked(cvApi.pdf).mockRejectedValueOnce(new Error("boom"));
    const wrapper = mountView();
    await flushPromises();
    await byText(wrapper.findAll("button"), "PDF EN")!.trigger("click");
    await flushPromises();
    expect(wrapper.find(".admin-page__error").text()).toContain("Export failed.");
  });
});
