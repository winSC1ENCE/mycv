import { beforeEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";
import { createPinia, setActivePinia } from "pinia";
import { useThemeStore } from "@/stores/theme";
import { useLocaleStore } from "@/stores/locale";
import { useCvStore } from "@/stores/cv";
import type { Cv } from "@/api/types";

describe("stores", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it("toggleFunny flips between normal and the available funny theme", () => {
    const store = useThemeStore();
    expect(store.theme).toBe("normal");
    expect(store.activeFunny).toBe("dog"); // default
    store.toggleFunny();
    expect(store.theme).toBe("dog");
    store.toggleFunny();
    expect(store.theme).toBe("normal");
  });

  it("toggleFunny uses the admin-selected funny theme", () => {
    const store = useThemeStore();
    store.setAvailableFunny("virus");
    store.toggleFunny();
    expect(store.theme).toBe("virus");
  });

  it("setTheme ignores a funny id that isn't the available one", () => {
    const store = useThemeStore();
    store.setAvailableFunny("dog");
    store.setTheme("virus"); // not the active funny theme → ignored
    expect(store.theme).toBe("normal");
    store.setTheme("dog");
    expect(store.theme).toBe("dog");
  });

  it("setAvailableFunny('none') drops a now-disallowed funny theme to normal", () => {
    const store = useThemeStore();
    store.toggleFunny(); // → dog
    expect(store.theme).toBe("dog");
    store.setAvailableFunny("none");
    expect(store.theme).toBe("normal");
    expect(store.funnyAvailable).toBe(false);
  });

  it("theme persists to localStorage and document dataset", async () => {
    const store = useThemeStore();
    store.toggleFunny();
    await nextTick();
    expect(localStorage.getItem("mycv:theme")).toBe("dog");
    expect(document.documentElement.dataset.theme).toBe("dog");
  });

  it("locale toggles between en and de", () => {
    const store = useLocaleStore();
    expect(store.locale).toBe("en");
    store.toggle();
    expect(store.locale).toBe("de");
    store.set("en");
    expect(store.locale).toBe("en");
  });

  it("timelineItems is empty when no CV is loaded", () => {
    const store = useCvStore();
    expect(store.timelineItems).toEqual([]);
  });

  it("timelineItems merges, sorts desc, links certificates by FK", () => {
    const store = useCvStore();
    store.cv = {
      id: 1,
      slug: "x",
      first_name: "",
      last_name: "",
      full_name: "",
      title: "",
      title_de: "",
      email: "",
      phone: "",
      location: "",
      address: "",
      zivilstand: "",
      zivilstand_de: "",
      date_of_birth: null,
      access_granted: false,
      summary: "",
      summary_de: "",
      photo: null,
      active_funny_theme: "dog",
      experiences: [
        {
          id: 10,
          role: "Engineer",
          role_de: "",
          company: "ACME",
          location: "",
          start_date: "2020-01-01",
          end_date: "2022-01-01",
          description: "",
          description_de: "",
          technologies: [],
          media: null,
          order: 0,
          is_published: true,
        },
      ],
      educations: [
        {
          id: 20,
          degree: "BSc",
          degree_de: "",
          institution: "Uni",
          location: "",
          start_date: "2016-08-01",
          end_date: "2019-06-01",
          description: "",
          description_de: "",
          technologies: [],
          media: null,
          order: 0,
          is_published: true,
        },
      ],
      certificates: [
        {
          id: 30,
          experience: 10,
          education: null,
          name: "Linked",
          name_de: "",
          issuer: "",
          issue_date: "2021-01-01",
          description: "",
          description_de: "",
          technologies: [],
          media: null,
          order: 0,
          is_published: true,
        },
        {
          id: 31,
          experience: null,
          education: null,
          name: "Standalone",
          name_de: "",
          issuer: "",
          issue_date: "2023-05-01",
          description: "",
          description_de: "",
          technologies: [],
          media: null,
          order: 0,
          is_published: true,
        },
      ],
      projects: [],
      social_links: [],
      timeline_entries: [
        {
          id: 40,
          date: "2024-12-01",
          kind: "milestone",
          title: "Now",
          title_de: "",
          description: "",
          description_de: "",
          order: 0,
          is_published: true,
        },
      ],
      skill_categories: [],
    } as Cv;

    const items = store.timelineItems;
    // 4 rows total: experience, education, standalone cert, milestone
    expect(items).toHaveLength(4);
    // Sorted descending by anchor date: milestone 2024-12 > standalone cert 2023-05 > experience 2022-01 > education 2019-06
    expect(items.map((r) => r.kind)).toEqual([
      "milestone",
      "certificate",
      "experience",
      "education",
    ]);
    // The experience row pulls in the linked cert
    const expRow = items.find((r) => r.kind === "experience");
    if (expRow?.kind === "experience") {
      expect(expRow.certs).toHaveLength(1);
      expect(expRow.certs[0].id).toBe(30);
    }
    // Standalone cert is a separate row, not in the experience row
    const certRow = items.find((r) => r.kind === "certificate");
    if (certRow?.kind === "certificate") {
      expect(certRow.data.id).toBe(31);
    }
  });

  it("timelineItems anchors current roles (end_date null) to today so they sort to the top", () => {
    const store = useCvStore();
    store.cv = {
      id: 1,
      slug: "x",
      first_name: "",
      last_name: "",
      full_name: "",
      title: "",
      title_de: "",
      email: "",
      phone: "",
      location: "",
      address: "",
      zivilstand: "",
      zivilstand_de: "",
      date_of_birth: null,
      access_granted: false,
      summary: "",
      summary_de: "",
      photo: null,
      active_funny_theme: "dog",
      experiences: [
        {
          id: 1,
          role: "Now",
          role_de: "",
          company: "",
          location: "",
          start_date: "2025-08-01",
          end_date: null,
          description: "",
          description_de: "",
          technologies: [],
          media: null,
          order: 0,
          is_published: true,
        },
      ],
      educations: [],
      certificates: [],
      projects: [],
      social_links: [],
      timeline_entries: [],
      skill_categories: [],
    } as Cv;
    const today = new Date().toISOString().slice(0, 10);
    expect(store.timelineItems[0].date).toBe(today);
  });
});
