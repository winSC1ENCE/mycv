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
  it("renders slot content unblurred when not blurred", () => {
    const wrapper = mountSensitive(false);
    expect(wrapper.text()).toBe("secret@example.com");
    expect(wrapper.classes()).not.toContain("sensitive--blurred");
    expect(wrapper.find(".sensitive__chip").exists()).toBe(false);
  });

  it("adds blurred class when blurred=true", () => {
    const wrapper = mountSensitive(true);
    expect(wrapper.classes()).toContain("sensitive--blurred");
  });

  it("renders a lock chip with data-tooltip when blurred", () => {
    const wrapper = mountSensitive(true);
    const chip = wrapper.find(".sensitive__chip");
    expect(chip.exists()).toBe(true);
    expect(chip.attributes("data-tooltip")).toBe("Order access via cv@chlous.top");
    expect(chip.find("svg[data-icon='lock']").exists()).toBe(true);
  });

  it("uses custom tooltip when provided", () => {
    const wrapper = mountSensitive(true, "Custom tooltip");
    expect(wrapper.find(".sensitive__chip").attributes("data-tooltip")).toBe(
      "Custom tooltip",
    );
  });

  it("sets aria-label on the chip for screen readers", () => {
    const wrapper = mountSensitive(true);
    expect(wrapper.find(".sensitive__chip").attributes("aria-label")).toBe(
      "Sensitive — request access via cv@chlous.top",
    );
  });

  it("has no chip when not blurred", () => {
    const wrapper = mountSensitive(false);
    expect(wrapper.find(".sensitive__chip").exists()).toBe(false);
  });

  it("does not set native title attribute (uses custom tooltip instead)", () => {
    const wrapper = mountSensitive(true);
    expect(wrapper.attributes("title")).toBeUndefined();
    expect(wrapper.find(".sensitive__chip").attributes("title")).toBeUndefined();
  });
});
