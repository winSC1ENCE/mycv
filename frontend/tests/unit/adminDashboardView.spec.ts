import { describe, expect, it, vi, beforeEach } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import en from "@/locales/en.json";

vi.mock("@/api/admin", () => ({
  cvApi: {
    pdf: vi.fn(async () => new Blob(["%PDF"], { type: "application/pdf" })),
    certificatesPdf: vi.fn(async () => new Blob(["%PDF"], { type: "application/pdf" })),
  },
}));

import AdminDashboardView from "@/views/admin/AdminDashboardView.vue";
import { cvApi } from "@/api/admin";

const i18n = createI18n({ legacy: false, locale: "en", messages: { en } });

function mountView() {
  return mount(AdminDashboardView, {
    global: { plugins: [i18n], stubs: { RouterLink: true } },
  });
}

function byText(buttons: ReturnType<ReturnType<typeof mountView>["findAll"]>, text: string) {
  return buttons.find((b) => b.text().includes(text));
}

beforeEach(() => {
  vi.clearAllMocks();
  global.URL.createObjectURL = vi.fn(() => "blob:x");
  global.URL.revokeObjectURL = vi.fn();
});

describe("AdminDashboardView exports", () => {
  it("exports the CV PDF in EN and DE", async () => {
    const wrapper = mountView();
    const rows = wrapper.findAll(".dashboard-exports__row");
    await byText(rows[0].findAll("button"), "EN")!.trigger("click");
    await flushPromises();
    expect(cvApi.pdf).toHaveBeenCalledWith("en", expect.any(String));

    await byText(rows[0].findAll("button"), "DE")!.trigger("click");
    await flushPromises();
    expect(cvApi.pdf).toHaveBeenCalledWith("de", expect.any(String));
    expect(global.URL.createObjectURL).toHaveBeenCalled();
  });

  it("exports the certificates PDF", async () => {
    const wrapper = mountView();
    const rows = wrapper.findAll(".dashboard-exports__row");
    await byText(rows[1].findAll("button"), "EN")!.trigger("click");
    await flushPromises();
    expect(cvApi.certificatesPdf).toHaveBeenCalledWith("en", expect.any(String));
  });

  it("surfaces an error when an export fails", async () => {
    vi.mocked(cvApi.certificatesPdf).mockRejectedValueOnce(new Error("boom"));
    const wrapper = mountView();
    const rows = wrapper.findAll(".dashboard-exports__row");
    await byText(rows[1].findAll("button"), "DE")!.trigger("click");
    await flushPromises();
    expect(wrapper.find(".admin-page__error").text()).toContain("Export failed.");
  });
});
