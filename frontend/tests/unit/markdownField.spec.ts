import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import MarkdownField from "@/components/base/MarkdownField.vue";

describe("MarkdownField.vue", () => {
  it("emits update on textarea input", async () => {
    const wrapper = mount(MarkdownField, { props: { modelValue: "" } });
    await wrapper.find("textarea").setValue("hello");
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["hello"]);
  });

  it("wraps the selection in bold markers via the toolbar", async () => {
    const wrapper = mount(MarkdownField, {
      props: { modelValue: "word" },
      attachTo: document.body,
    });
    const el = wrapper.find("textarea").element as HTMLTextAreaElement;
    el.setSelectionRange(0, 4);
    await wrapper.find('button[title="Bold"]').trigger("click");
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["**word**"]);
    wrapper.unmount();
  });

  it("inserts a list marker at the line start", async () => {
    const wrapper = mount(MarkdownField, {
      props: { modelValue: "item" },
      attachTo: document.body,
    });
    const el = wrapper.find("textarea").element as HTMLTextAreaElement;
    el.setSelectionRange(4, 4);
    await wrapper.find('button[title="Bullet list"]').trigger("click");
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["- item"]);
    wrapper.unmount();
  });

  it("toggles to a preview rendering the markdown", async () => {
    const wrapper = mount(MarkdownField, { props: { modelValue: "**hi**" } });
    expect(wrapper.find("textarea").exists()).toBe(true);
    await wrapper.find(".md-field__toggle").trigger("click");
    expect(wrapper.find("textarea").exists()).toBe(false);
    expect(wrapper.find(".rich-text strong").text()).toBe("hi");
  });
});
