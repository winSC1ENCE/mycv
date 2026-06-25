<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from "vue";
import { storeToRefs } from "pinia";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useI18n } from "vue-i18n";
import { useCvStore, type TimelineRow } from "@/stores/cv";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import { useEscClose } from "@/composables/useEscClose";
import { formatMonthYear } from "@/utils/dateFormat";
import { iconForTheme } from "@/composables/useThemeIcon";
import { petCount, spawnBubble } from "@/composables/useFunBubbles";
import { useThemeStore } from "@/stores/theme";
import { packFor } from "@/themes/registry";
import TimelineDetail from "./TimelineDetail.vue";

gsap.registerPlugin(ScrollTrigger);

const cvStore = useCvStore();
const { timelineItems } = storeToRefs(cvStore);
const { locale } = storeToRefs(useLocaleStore());
const { theme } = storeToRefs(useThemeStore());
const { t } = useI18n();

const openId = ref<string | null>(null);
const root = ref<HTMLElement | null>(null);

useEscClose(
  () => {
    openId.value = null;
  },
  computed(() => openId.value !== null),
);

function uid(row: TimelineRow): string {
  return `${row.kind}-${row.data.id}`;
}

const funPack = computed(() => packFor(theme.value));

function nodeStyle(row: TimelineRow): Record<string, string> {
  return { "--node-icon": `url('${iconForTheme(theme.value, uid(row))}')` };
}

function onNodeClick(ev: MouseEvent, row: TimelineRow): void {
  if (!funPack.value) return;
  spawnBubble(
    theme.value,
    locale.value,
    ev.clientX,
    ev.clientY,
    iconForTheme(theme.value, uid(row)),
  );
}

const counterText = computed(() => {
  const pack = funPack.value;
  if (!pack) return "";
  return `${pack.emoji} ${t(pack.counterKey, { n: petCount.value })}`;
});

function headline(row: TimelineRow): string {
  switch (row.kind) {
    case "experience":
      return pickLocalized(row.data, "role", locale.value);
    case "education":
      return pickLocalized(row.data, "degree", locale.value);
    case "certificate":
      return pickLocalized(row.data, "name", locale.value);
    case "milestone":
      return pickLocalized(row.data, "title", locale.value);
  }
}

function subline(row: TimelineRow): string {
  switch (row.kind) {
    case "experience":
      return row.data.company;
    case "education":
      return row.data.institution;
    case "certificate":
      return row.data.issuer;
    case "milestone":
      return row.data.kind;
  }
}

type AxisDates =
  | { range: true; start: string; end: string | null }
  | { range: false; single: string };

function axisDates(row: TimelineRow): AxisDates {
  switch (row.kind) {
    case "experience":
    case "education":
      return { range: true, start: row.data.start_date, end: row.data.end_date };
    case "certificate":
      return { range: false, single: row.data.issue_date };
    case "milestone":
      return { range: false, single: row.data.date };
  }
}

function fmtMY(iso: string): string {
  return formatMonthYear(iso, locale.value);
}

function toggle(id: string, ev: Event): void {
  openId.value = openId.value === id ? null : id;
  if (openId.value) {
    const el = (ev.currentTarget as HTMLElement).closest(".timeline__row");
    if (el) nextTick(() => el.scrollIntoView({ behavior: "smooth", block: "nearest" }));
  }
}

let triggers: ScrollTrigger[] = [];

onMounted(() => {
  if (typeof window === "undefined") return;
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced || !root.value) return;
  nextTick(() => {
    const rows = root.value?.querySelectorAll(".timeline__row") ?? [];
    rows.forEach((row) => {
      const trigger = gsap.from(row, {
        opacity: 0,
        y: 24,
        duration: 0.55,
        ease: "power2.out",
        scrollTrigger: {
          trigger: row,
          start: "top 88%",
          toggleActions: "play none none none",
        },
      }).scrollTrigger;
      if (trigger) triggers.push(trigger);
    });
  });
});

onUnmounted(() => {
  triggers.forEach((t) => t.kill());
  triggers = [];
});

const rows = computed(() => timelineItems.value.map((row) => ({ row, axis: axisDates(row) })));

const hasItems = computed(() => timelineItems.value.length > 0);
</script>

<template>
  <section class="section" aria-labelledby="timeline-title">
    <div class="container">
      <h2 id="timeline-title" class="section__title">{{ t("timeline.title") }}</h2>
      <p class="section__lead">{{ t("timeline.lead") }}</p>
      <ol v-if="hasItems" ref="root" class="timeline timeline--alt" role="list">
        <li
          v-for="({ row, axis }, i) in rows"
          :key="uid(row)"
          class="timeline__row"
          :class="[
            `timeline__row--${row.kind}`,
            i % 2 === 0 ? 'timeline__row--left' : 'timeline__row--right',
          ]"
        >
          <span
            class="timeline__node"
            :style="nodeStyle(row)"
            :data-kind="row.kind"
            aria-hidden="true"
            @click="(ev) => onNodeClick(ev, row)"
          />
          <time class="timeline__date" :datetime="row.date">
            <template v-if="axis.range">
              <span class="timeline__date-part">{{ fmtMY(axis.start) }}</span>
              <span class="timeline__date-sep" aria-hidden="true">–</span>
              <span class="timeline__date-part timeline__date-part--end">
                {{ axis.end ? fmtMY(axis.end) : $t("labels.present") }}
              </span>
            </template>
            <span v-else class="timeline__date-part">{{ fmtMY(axis.single) }}</span>
          </time>
          <article class="timeline__card">
            <button
              class="timeline__card-toggle"
              type="button"
              :aria-expanded="openId === uid(row)"
              :aria-controls="`${uid(row)}-detail`"
              @click="(ev) => toggle(uid(row), ev)"
            >
              <span class="timeline__card-text">
                <span class="timeline__kind">{{ t(`timeline.kind.${row.kind}`) }}</span>
                <h3 class="timeline__card-title">{{ headline(row) }}</h3>
                <p class="timeline__card-sub">{{ subline(row) }}</p>
              </span>
              <span class="timeline__chevron" aria-hidden="true">▾</span>
            </button>
            <div v-if="openId === uid(row)" :id="`${uid(row)}-detail`" class="timeline__detail">
              <TimelineDetail :row="row" />
            </div>
          </article>
        </li>
      </ol>
      <p v-else class="timeline__empty">{{ t("timeline.empty") }}</p>
      <div v-if="funPack && petCount > 0" class="dog-pet-counter" aria-hidden="true">
        {{ counterText }}
      </div>
    </div>
  </section>
</template>
