<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { gsap } from "gsap";
import type { Cv } from "@/api/types";
import { useLocaleStore } from "@/stores/locale";
import { storeToRefs } from "pinia";
import { pickLocalized } from "@/composables/useLocalized";

const props = defineProps<{ cv: Cv }>();
const { locale } = storeToRefs(useLocaleStore());

interface Item {
  id: string;
  date: string;
  title: string;
  subtitle: string;
}

const items = computed<Item[]>(() => {
  const entries: Item[] = [];
  for (const exp of props.cv.experiences) {
    entries.push({
      id: `exp-${exp.id}`,
      date: exp.start_date,
      title: pickLocalized(exp, "role", locale.value),
      subtitle: exp.company,
    });
  }
  for (const edu of props.cv.educations) {
    entries.push({
      id: `edu-${edu.id}`,
      date: edu.start_date,
      title: pickLocalized(edu, "degree", locale.value),
      subtitle: edu.institution,
    });
  }
  for (const cert of props.cv.certificates) {
    entries.push({
      id: `cert-${cert.id}`,
      date: cert.issue_date,
      title: pickLocalized(cert, "name", locale.value),
      subtitle: cert.issuer,
    });
  }
  for (const tl of props.cv.timeline_entries) {
    entries.push({
      id: `tl-${tl.id}`,
      date: tl.date,
      title: pickLocalized(tl, "title", locale.value),
      subtitle: tl.kind,
    });
  }
  return entries.sort((a, b) => b.date.localeCompare(a.date));
});

const root = ref<HTMLElement | null>(null);

onMounted(() => {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced || !root.value) return;
  const els = root.value.querySelectorAll(".timeline__item");
  gsap.from(els, {
    opacity: 0,
    x: -20,
    duration: 0.5,
    stagger: 0.06,
    ease: "power2.out",
  });
});
</script>

<template>
  <section class="section" aria-labelledby="timeline-title">
    <div class="container">
      <h2 id="timeline-title" class="section__title">Timeline</h2>
      <div ref="root" class="timeline">
        <article v-for="item in items" :key="item.id" class="timeline__item">
          <div class="timeline__item-card">
            <p class="timeline__date">{{ item.date }}</p>
            <h3>{{ item.title }}</h3>
            <p>{{ item.subtitle }}</p>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
