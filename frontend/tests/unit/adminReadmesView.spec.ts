import { describe, expect, it, vi, beforeEach } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import en from "@/locales/en.json";

vi.mock("@/api/admin", () => ({
  readmeApi: {
    list: vi.fn(async () => ({ results: [] })),
    create: vi.fn(async (p: object) => ({ id: 1, ...p })),
    update: vi.fn(async (id: number, p: object) => ({ id, ...p })),
    destroy: vi.fn(async () => {}),
    pdf: vi.fn(async () => new Blob(["%PDF"], { type: "application/pdf" })),
  },
  accessKeyApi: {
    list: vi.fn(async () => ({ results: [] })),
  },
}));

import AdminReadmesView from "@/views/admin/AdminReadmesView.vue";
import { readmeApi } from "@/api/admin";

const i18n = createI18n({ legacy: false, locale: "en", messages: { en } });

function mountView() {
  return mount(AdminReadmesView, {
    global: { plugins: [i18n], stubs: { RouterLink: { template: "<a><slot/></a>" } } },
  });
}

function byText(buttons: ReturnType<ReturnType<typeof mountView>["findAll"]>, text: string) {
  return buttons.find((b) => b.text().includes(text));
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("AdminReadmesView", () => {
  it("loads the list on mount", async () => {
    const wrapper = mountView();
    await flushPromises();
    expect(readmeApi.list).toHaveBeenCalled();
    expect(wrapper.text()).toContain("Applications");
  });

  it("prefills the body from the starter template", async () => {
    const wrapper = mountView();
    await flushPromises();
    byText(wrapper.findAll("button"), "Add")!.trigger("click");
    await flushPromises();
    byText(wrapper.findAll("button"), "New from template")!.trigger("click");
    await flushPromises();
    expect(wrapper.find("textarea").element.value).toContain("Quick Start");
    expect(wrapper.find("textarea").element.value).toContain("{{access_url}}");
  });

  it("sorts the list by name when the Name header is clicked", async () => {
    const row = (id: number, name: string, created_at: string) => ({
      id,
      name,
      created_at,
      version: "v1.0.0",
      is_published: true,
      content: "",
      content_de: "",
      letter_content: "",
      letter_content_de: "",
      letter_reference: "",
      access_key: null,
      access_url: "",
      expires_display: "",
      updated_display: "",
      order: 0,
      updated_at: created_at,
    });
    vi.mocked(readmeApi.list).mockResolvedValueOnce({
      count: 2,
      next: null,
      previous: null,
      results: [
        row(1, "Zeta GmbH", "2026-01-01T00:00:00Z"),
        row(2, "Alpha AG", "2026-02-01T00:00:00Z"),
      ],
    });
    const wrapper = mountView();
    await flushPromises();

    const nameHeader = byText(wrapper.findAll("th"), "Name")!;
    await nameHeader.trigger("click"); // ascending
    await flushPromises();
    expect(wrapper.findAll("tbody tr")[0].text()).toContain("Alpha AG");

    await nameHeader.trigger("click"); // descending
    await flushPromises();
    expect(wrapper.findAll("tbody tr")[0].text()).toContain("Zeta GmbH");
  });

  it("creates a README on save", async () => {
    const wrapper = mountView();
    await flushPromises();
    byText(wrapper.findAll("button"), "Add")!.trigger("click");
    await flushPromises();
    await wrapper.find("input").setValue("ACME GmbH");
    await wrapper.find("form").trigger("submit");
    await flushPromises();
    expect(readmeApi.create).toHaveBeenCalledWith(expect.objectContaining({ name: "ACME GmbH" }));
  });
});
