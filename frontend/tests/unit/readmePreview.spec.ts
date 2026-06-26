import { describe, expect, it } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import ReadmePreview from "@/components/base/ReadmePreview.vue";
import type { ReadmeContext } from "@/utils/readme";

const CTX: ReadmeContext = {
  accessUrl: "https://cv.test/?key=abc",
  expiresAt: "30.06.2026 23:59",
  version: "v2.3.4",
  updated: "26.06.2026",
};

describe("ReadmePreview", () => {
  it("renders the name and version/updated badges", async () => {
    const wrapper = mount(ReadmePreview, {
      props: { name: "ACME GmbH", markdown: "# Hello", ctx: CTX },
    });
    await flushPromises();
    expect(wrapper.text()).toContain("ACME GmbH");
    expect(wrapper.text()).toContain("v2.3.4");
    expect(wrapper.text()).toContain("26.06.2026");
  });

  it("renders the substituted markdown body", async () => {
    const wrapper = mount(ReadmePreview, {
      props: { name: "X", markdown: "Open {{access_url}} now", ctx: CTX },
    });
    await flushPromises();
    expect(wrapper.find(".readme-preview__body").html()).toContain("https://cv.test/?key=abc");
  });
});
