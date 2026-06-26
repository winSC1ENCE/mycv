/**
 * Virus Mode theme pack — epidemiology / national-surveillance gag.
 *
 * Additive overlay: real CV data is untouched. This pack supplies the timeline
 * node icons + click bubbles, per-skill hover quips, a themed profile hero
 * block, and an easter-egg modal (R₀ reproduction-number panel). Surrounding
 * copy lives in i18n under `themes.virus.*` (DE+EN); skill quips are colocated
 * here as a per-language map.
 */

import type { ThemePack } from "./types";

const VIRUS_ICONS = [
  "/icons/virus/virus.svg",
  "/icons/virus/microscope.svg",
  "/icons/virus/dna.svg",
  "/icons/virus/test-tube.svg",
  "/icons/virus/syringe.svg",
  "/icons/virus/biohazard.svg",
  "/icons/virus/mask.svg",
  "/icons/virus/petri.svg",
] as const;

export const virusPack: ThemePack = {
  id: "virus",
  label: "Virus",
  emoji: "🦠",
  profilePhoto: "/profile-virus.jpg",
  counterKey: "themes.virus.counter",
  nodeIcons: VIRUS_ICONS,
  phrases: {
    en: {
      iconPhrases: {
        virus: ["R₀ ↑", "MUTATED!", "OUTBREAK!", "VIRAL!"],
        microscope: ["DETECTED!", "FINDING!", "SAMPLE +", "ANALYSIS…"],
        dna: ["SEQUENCED!", "MUTATED!", "STRAND +", "CODE!"],
        "test-tube": ["POSITIVE!", "REACTS!", "BLOOP!", "SAMPLE!"],
        syringe: ["VACCINATED!", "DOSE!", "JAB!", "IMMUNE!"],
        biohazard: ["DANGER!", "CONTAMINATED!", "ALERT!", "QUARANTINE ZONE!"],
        mask: ["MASK ON!", "FFP2!", "PROTECTS!", "DISTANCE!"],
        petri: ["CULTURE!", "GROWING!", "COLONY!", "DIVIDING!"],
      },
      defaultPhrases: ["INFECTED!", "QUARANTINE!", "CONTAINED!", "NOTIFIABLE!", "PANDEMIC!"],
      praise: {
        3: "PATIENT ZERO!",
        7: "SUPERSPREADER!",
        15: "PANDEMIC!",
        30: "WHO ALERT!",
      },
    },
    de: {
      iconPhrases: {
        virus: ["R₀ ↑", "MUTIERT!", "AUSBRUCH!", "VIRAL!"],
        microscope: ["ENTDECKT!", "BEFUND!", "PROBE +", "ANALYSE…"],
        dna: ["SEQUENZIERT!", "MUTIERT!", "STRANG +", "CODE!"],
        "test-tube": ["POSITIV!", "REAGIERT!", "BLUBB!", "PROBE!"],
        syringe: ["GEIMPFT!", "DOSIS!", "PIKS!", "IMMUN!"],
        biohazard: ["GEFAHR!", "KONTAMINIERT!", "ALARM!", "SPERRZONE!"],
        mask: ["MASKE AUF!", "FFP2!", "SCHÜTZT!", "ABSTAND!"],
        petri: ["KULTUR!", "WÄCHST!", "KOLONIE!", "TEILT SICH!"],
      },
      defaultPhrases: ["INFIZIERT!", "QUARANTÄNE!", "EINGEDÄMMT!", "MELDEPFLICHT!", "PANDEMIE!"],
      praise: {
        3: "PATIENT NULL!",
        7: "SUPERSPREADER!",
        15: "PANDEMIE!",
        30: "WHO-ALARM!",
      },
    },
  },
  skillQuips: {
    Python: {
      en: "Efficacy against data chaos: 99.7 %",
      de: "Wirksamkeit gegen Datenchaos: 99.7 %",
    },
    SQL: {
      en: "Broad-spectrum antibiotic for relational ailments",
      de: "Breitbandantibiotikum gegen relationale Probleme",
    },
    "T-SQL": {
      en: "Broad-spectrum antibiotic for relational ailments",
      de: "Breitbandantibiotikum gegen relationale Probleme",
    },
    Docker: {
      en: "Reliably isolates applications in containers",
      de: "Isoliert Anwendungen zuverlässig in Containern",
    },
    PySpark: {
      en: "Distributes the treatment across the whole cluster",
      de: "Verteilt die Behandlung auf den ganzen Cluster",
    },
    Airflow: {
      en: "Orchestrates containment on schedule",
      de: "Orchestriert die Eindämmung nach Zeitplan",
    },
    NiFi: {
      en: "Channels the data stream into safe pathways",
      de: "Lenkt den Datenstrom in sichere Bahnen",
    },
    Git: {
      en: "Full contact-tracing of every change",
      de: "Lückenlose Kontaktnachverfolgung jeder Änderung",
    },
  },
  hero: {
    leadKey: "themes.virus.profile.lead",
    itemsKey: "themes.virus.profile.items",
  },
  easterEgg: {
    buttonKey: "themes.virus.egg.button",
    titleKey: "themes.virus.egg.title",
    introKey: "themes.virus.egg.intro",
    footnoteKey: "themes.virus.egg.footnote",
    valueHeadKey: "themes.virus.egg.valueHead",
    rows: [
      { labelKey: "themes.virus.egg.rows.python", value: "6.9" },
      { labelKey: "themes.virus.egg.rows.sql", value: "4.1" },
      { labelKey: "themes.virus.egg.rows.automation", value: "5.7" },
    ],
  },
};
