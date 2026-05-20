import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import Sensitive from "@/components/base/Sensitive.vue";

const i18n = createI18n({
  legacy: false,
  locale: "en",
  messages: {
    en: {
      sensitive: {
        tooltip: "Order access via cv{'@'}chlous.top",
        ariaLabel: "Sensitive — request access via cv{'@'}chlous.top",
      },
    },
  },
});

function mountSensitive(blurred: boolean, tooltip?: string) {
  return mount(Sensitive, {
    global: { plugins: [i18n] },
    props: { blurred, ...(tooltip ? { tooltip } : {}) },
    slots: { default: "secret@example.com" },
  });
}

describe("Sensitive.vue", () => {
  it("renders slot content when not blurred", () => {
    const wrapper = mountSensitive(false);
    expect(wrapper.text()).toBe("secret@example.com");
    expect(wrapper.classes()).not.toContain("sensitive--blurred");
    expect(wrapper.attributes("title")).toBeUndefined();
  });

  it("adds blurred class when blurred=true", () => {
    const wrapper = mountSensitive(true);
    expect(wrapper.classes()).toContain("sensitive--blurred");
  });

  it("shows default tooltip from i18n when blurred", () => {
    const wrapper = mountSensitive(true);
    expect(wrapper.attributes("title")).toBe("Order access via cv@chlous.top");
  });

  it("shows custom tooltip when provided", () => {
    const wrapper = mountSensitive(true, "Custom tooltip");
    expect(wrapper.attributes("title")).toBe("Custom tooltip");
  });

  it("sets aria-label when blurred for screen readers", () => {
    const wrapper = mountSensitive(true);
    expect(wrapper.attributes("aria-label")).toBe(
      "Sensitive — request access via cv@chlous.top",
    );
  });

  it("has no aria-label when not blurred", () => {
    const wrapper = mountSensitive(false);
    expect(wrapper.attributes("aria-label")).toBeUndefined();
  });
});
