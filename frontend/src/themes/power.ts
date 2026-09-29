/**
 * Power Mode theme pack — electrical-power superhero comic-book style.
 *
 * High-voltage energy: a glowing spark backdrop, a bolt/warning/tower/bulb/
 * windmill/spark timeline icon set, and a bolt mark on the header brand +
 * favicon. Follows the dog.ts / virus.ts shape.
 */

import type { ThemePack } from "./types";

const POWER_ICONS = [
  "/icons/power/bolt.svg",
  "/icons/power/warning.svg",
  "/icons/power/tower.svg",
  "/icons/power/bulb.svg",
  "/icons/power/windmill.svg",
  "/icons/power/spark.svg",
] as const;

export const powerPack: ThemePack = {
  id: "power",
  label: "Power",
  emoji: "⚡",
  profilePhoto: "/profile-power.jpg",
  counterKey: "themes.power.counter",
  nodeIcons: POWER_ICONS,
  photoAltFallback: "Nicolas Mischler — electric portrait",
  brandIcon: "bolt",
  favicon: "/icons/power/app-icon-power.svg",
  phrases: {
    en: {
      iconPhrases: {
        bolt: ["ZAP!", "ZOT!", "STRIKE!", "CRACKLE!"],
        warning: ["HIGH VOLTAGE!", "DANGER!", "CAUTION!", "LIVE WIRE!"],
        tower: ["GRID LIVE!", "TRANSMITTING!", "LINES UP!", "POWERED GRID!"],
        bulb: ["LIGHTS ON!", "BRIGHT IDEA!", "GLOWING!", "ILLUMINATED!"],
        windmill: ["SPINNING!", "CLEAN POWER!", "WIND POWER!", "RENEWABLE!"],
        spark: ["FLASH!", "JOLT!", "QUICK ZAP!", "SPARKLE!"],
      },
      defaultPhrases: ["SPARK!", "SHORT CIRCUIT!", "HIGH VOLTAGE!", "AMPED!", "ELECTRIFYING!"],
      praise: {
        3: "FULLY CHARGED!",
        7: "HIGH VOLTAGE!",
        15: "SUPERCHARGED!",
        30: "CIRCUIT MASTER!",
      },
    },
    de: {
      iconPhrases: {
        bolt: ["ZACK!", "BLITZ!", "TREFFER!", "KNISTER!"],
        warning: ["HOCHSPANNUNG!", "GEFAHR!", "VORSICHT!", "UNTER STROM!"],
        tower: ["NETZ LIVE!", "ÜBERTRAGUNG!", "LEITUNG STEHT!", "NETZ AKTIV!"],
        bulb: ["LICHT AN!", "GUTE IDEE!", "LEUCHTET!", "ERHELLT!"],
        windmill: ["DREHT SICH!", "ÖKOSTROM!", "WINDKRAFT!", "ERNEUERBAR!"],
        spark: ["BLITZ!", "RUCK!", "SCHNELLER ZAP!", "FUNKELN!"],
      },
      defaultPhrases: ["FUNKE!", "KURZSCHLUSS!", "HOCHSPANNUNG!", "GELADEN!", "ELEKTRISIEREND!"],
      praise: {
        3: "VOLL GELADEN!",
        7: "HOCHSPANNUNG!",
        15: "AUFGELADEN!",
        30: "STROM-MEISTER!",
      },
    },
  },
  skillQuips: {
    Python: {
      en: "Runs at full voltage through data chaos",
      de: "Läuft mit voller Spannung durch das Datenchaos",
    },
    SQL: {
      en: "Wired straight into relational circuits",
      de: "Direkt in relationale Schaltkreise verdrahtet",
    },
    "T-SQL": {
      en: "Wired straight into relational circuits",
      de: "Direkt in relationale Schaltkreise verdrahtet",
    },
    Docker: {
      en: "Contains the current safely in every container",
      de: "Hält den Strom sicher in jedem Container",
    },
    PySpark: {
      en: "Distributes the charge across the whole cluster",
      de: "Verteilt die Ladung auf den ganzen Cluster",
    },
    Airflow: {
      en: "Switches the grid on schedule, no blackouts",
      de: "Schaltet das Netz nach Zeitplan, ohne Stromausfall",
    },
    NiFi: {
      en: "Routes the current through safe conduits",
      de: "Leitet den Strom durch sichere Leitungen",
    },
    Git: {
      en: "Every change logged on the circuit diagram",
      de: "Jede Änderung im Schaltplan dokumentiert",
    },
  },
  hero: {
    leadKey: "themes.power.profile.lead",
    itemsKey: "themes.power.profile.items",
  },
  easterEgg: {
    buttonKey: "themes.power.egg.button",
    titleKey: "themes.power.egg.title",
    introKey: "themes.power.egg.intro",
    footnoteKey: "themes.power.egg.footnote",
    valueHeadKey: "themes.power.egg.valueHead",
    rows: [
      { labelKey: "themes.power.egg.rows.python", value: "220V" },
      { labelKey: "themes.power.egg.rows.sql", value: "180V" },
      { labelKey: "themes.power.egg.rows.automation", value: "240V" },
    ],
  },
};
