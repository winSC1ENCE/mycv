import { afterEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";
import { mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import EasterEggModal from "@/components/base/EasterEggModal.vue";
import { virusPack } from "@/themes/virus";

const i18n = createI18n({
  legacy: false,
  locale: "en",
  messages: {
    en: {
      actions: { close: "Close" },
      themes: {
        virus: {
          egg: {
            button: "Trace pathogens",
            title: "National Surveillance System",
            intro: "R0 spread:",
            valueHead: "R0",
            footnote: "Spreads best practices at epidemic speed.",
            rows: { python: "Python knowledge", sql: "SQL skills", automation: "Automation" },
          },
        },
      },
    },
  },
});

function mountModal(open: boolean) {
  return mount(EasterEggModal, {
    global: { plugins: [i18n] },
    props: { open, egg: virusPack.easterEgg! },
    attachTo: document.body,
  });
}

afterEach(() => {
  document.body.innerHTML = "";
});

describe("EasterEggModal", () => {
  it("renders the surveillance title and one row per easter-egg row when open", () => {
    mountModal(true);
    expect(document.body.textContent).toContain("National Surveillance System");
    expect(document.body.querySelectorAll(".egg-table tbody tr")).toHaveLength(
      virusPack.easterEgg!.rows.length,
    );
    const pythonValue = virusPack.easterEgg!.rows.find((r) => r.labelKey.endsWith("python"))!.value;
    expect(document.body.textContent).toContain(pythonValue);
  });

  it("renders nothing when closed", () => {
    mountModal(false);
    expect(document.body.querySelector(".egg-modal")).toBeNull();
  });

  it("emits update:open=false when the close button is clicked", async () => {
    const wrapper = mountModal(true);
    // The modal teleports to <body>, so query the document, not the wrapper.
    const closeBtn = document.body.querySelector<HTMLButtonElement>(".egg-modal__close");
    expect(closeBtn).not.toBeNull();
    closeBtn!.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    await nextTick();
    expect(wrapper.emitted("update:open")?.[0]).toEqual([false]);
  });
});
