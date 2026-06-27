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
  it("renders the manual heading and expands {{badges}} into version/updated chips", async () => {
    const wrapper = mount(ReadmePreview, {
      props: { markdown: "# My Title\n\n{{badges}}", ctx: CTX },
    });
    await flushPromises();
    const body = wrapper.find(".readme-preview__body").html();
    expect(body).toContain("<h1>My Title</h1>");
    expect(body).toContain("readme-badges");
    expect(wrapper.text()).toContain("v2.3.4");
    expect(wrapper.text()).toContain("26.06.2026");
  });

  it("renders the substituted markdown body", async () => {
    const wrapper = mount(ReadmePreview, {
      props: { markdown: "Open {{access_url}} now", ctx: CTX },
    });
    await flushPromises();
    expect(wrapper.find(".readme-preview__body").html()).toContain("https://cv.test/?key=abc");
  });
});
