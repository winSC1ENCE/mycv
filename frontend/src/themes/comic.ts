/**
 * Comic Mode theme pack — electrical-power superhero comic-book style.
 *
 * High-voltage energy: halftone dots, bolt/POW timeline icons, and a bolt
 * mark on the header brand + favicon. Follows the dog.ts / virus.ts shape.
 */

import type { ThemePack } from "./types";

const COMIC_ICONS = [
  "/icons/comic/bolt.svg",
  "/icons/comic/pow.svg",
  "/icons/comic/zap-burst.svg",
  "/icons/comic/battery.svg",
  "/icons/comic/plug.svg",
  "/icons/comic/star-burst.svg",
  "/icons/comic/thunder-cloud.svg",
  "/icons/comic/boom.svg",
] as const;

export const comicPack: ThemePack = {
  id: "comic",
  label: "Comic",
  emoji: "⚡",
  profilePhoto: "/profile-comic.jpg",
  counterKey: "themes.comic.counter",
  nodeIcons: COMIC_ICONS,
  photoAltFallback: "Nicolas Mischler — electric portrait",
  brandIcon: "bolt",
  favicon: "/icons/comic/app-icon-comic.svg",
  phrases: {
    en: {
      iconPhrases: {
        bolt: ["ZAP!", "ZOT!", "STRIKE!", "CRACKLE!"],
        pow: ["POW!", "BAM!", "WHAM!", "SMACK!"],
        "zap-burst": ["ZZZAP!", "SURGE!", "FLASH!", "OVERLOAD!"],
        battery: ["CHARGED!", "TOPPED UP!", "FULL POWER!", "JUICED!"],
        plug: ["PLUGGED IN!", "CONNECTED!", "LIVE WIRE!", "ONLINE!"],
        "star-burst": ["KA-POW!", "BOOM!", "BLAST!", "IMPACT!"],
        "thunder-cloud": ["RUMBLE!", "STORM!", "BRACE!", "INCOMING!"],
        boom: ["KABOOM!", "BLAM!", "DETONATE!", "SHAZAM!"],
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
        pow: ["WUMM!", "BUMM!", "WHAM!", "KLATSCH!"],
        "zap-burst": ["ZZZAP!", "SCHUB!", "BLITZ!", "ÜBERLASTUNG!"],
        battery: ["GELADEN!", "AUFGELADEN!", "VOLLE KRAFT!", "GESTÄRKT!"],
        plug: ["EINGESTECKT!", "VERBUNDEN!", "UNTER STROM!", "ONLINE!"],
        "star-burst": ["KA-WUMM!", "BUMM!", "EXPLOSION!", "EINSCHLAG!"],
        "thunder-cloud": ["GRUMMEL!", "GEWITTER!", "ACHTUNG!", "ES NAHT!"],
        boom: ["KABUMM!", "KRACH!", "ZÜNDUNG!", "SCHAZAM!"],
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
    leadKey: "themes.comic.profile.lead",
    itemsKey: "themes.comic.profile.items",
  },
  easterEgg: {
    buttonKey: "themes.comic.egg.button",
    titleKey: "themes.comic.egg.title",
    introKey: "themes.comic.egg.intro",
    footnoteKey: "themes.comic.egg.footnote",
    valueHeadKey: "themes.comic.egg.valueHead",
    rows: [
      { labelKey: "themes.comic.egg.rows.python", value: "220V" },
      { labelKey: "themes.comic.egg.rows.sql", value: "180V" },
      { labelKey: "themes.comic.egg.rows.automation", value: "240V" },
    ],
  },
};
