import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import RichText from "@/components/base/RichText.vue";

describe("RichText.vue", () => {
  it("renders markdown as sanitized HTML", () => {
    const wrapper = mount(RichText, { props: { text: "**bold**\n\n- a\n- b" } });
    expect(wrapper.find("strong").text()).toBe("bold");
    expect(wrapper.findAll("li")).toHaveLength(2);
  });

  it("renders nothing for empty text", () => {
    const wrapper = mount(RichText, { props: { text: "" } });
    expect(wrapper.find(".rich-text").html()).not.toContain("<p>");
  });

  it("strips dangerous html", () => {
    const wrapper = mount(RichText, { props: { text: "x <script>alert(1)</script>" } });
    expect(wrapper.html()).not.toContain("<script>");
  });
});
