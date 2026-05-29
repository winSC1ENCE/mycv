import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import Icon, { type IconName } from "@/components/base/Icon.vue";

const ALL_NAMES: IconName[] = ["map-pin", "heart", "cake", "lock", "mail", "phone", "github"];

describe("Icon.vue", () => {
  it.each(ALL_NAMES)("renders an svg with the expected data-icon for '%s'", (name) => {
    const wrapper = mount(Icon, { props: { name } });
    const svg = wrapper.find("svg");
    expect(svg.exists()).toBe(true);
    expect(svg.attributes("data-icon")).toBe(name);
    expect(svg.find("path").exists()).toBe(true);
    expect(svg.find("path").attributes("d")).toBeTruthy();
  });

  it("honours the size prop", () => {
    const wrapper = mount(Icon, { props: { name: "lock", size: 32 } });
    const svg = wrapper.find("svg");
    expect(svg.attributes("width")).toBe("32");
    expect(svg.attributes("height")).toBe("32");
  });

  it("defaults to size 16", () => {
    const wrapper = mount(Icon, { props: { name: "lock" } });
    expect(wrapper.find("svg").attributes("width")).toBe("16");
    expect(wrapper.find("svg").attributes("height")).toBe("16");
  });

  it("inherits color via currentColor (stroke attribute)", () => {
    const wrapper = mount(Icon, { props: { name: "heart" } });
    expect(wrapper.find("svg").attributes("stroke")).toBe("currentColor");
  });

  it("sets aria-hidden by default", () => {
    const wrapper = mount(Icon, { props: { name: "lock" } });
    expect(wrapper.find("svg").attributes("aria-hidden")).toBe("true");
  });

  it("omits aria-hidden when ariaHidden=false", () => {
    const wrapper = mount(Icon, { props: { name: "lock", ariaHidden: false } });
    expect(wrapper.find("svg").attributes("aria-hidden")).toBeUndefined();
  });
});
