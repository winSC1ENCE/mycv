<script setup lang="ts">
import { computed } from "vue";
import { storeToRefs } from "pinia";
import { useI18n } from "vue-i18n";
import { useLocaleStore } from "@/stores/locale";
import { useThemeStore } from "@/stores/theme";
import { pickLocalized } from "@/composables/useLocalized";
import { useLevelLabel } from "@/composables/useLevelLabel";
import { packFor } from "@/themes/registry";
import type { SkillCategory } from "@/api/types";

defineProps<{ categories: SkillCategory[] }>();
const { locale } = storeToRefs(useLocaleStore());
const { theme } = storeToRefs(useThemeStore());
const { t } = useI18n();
const levelLabel = useLevelLabel();

// Themed hover quips (e.g. Virus Mode). Returns "" when the active theme has none.
const quips = computed(() => packFor(theme.value)?.skillQuips ?? null);
function quipFor(name: string): string {
  const q = quips.value?.[name];
  if (!q) return "";
  return locale.value === "de" ? q.de : q.en;
}
</script>

<template>
  <section class="section" aria-labelledby="skills-title">
    <div class="container">
      <h2 id="skills-title" class="section__title">{{ $t("nav.skills") }}</h2>
      <div class="grid grid--2">
        <article v-for="cat in categories" :key="cat.id" class="card skill-card">
          <h3 class="skill-card__title">{{ pickLocalized(cat, "name", locale) }}</h3>
          <ul class="skill-list">
            <li v-for="skill in cat.skills" :key="skill.id" class="skill-row">
              <strong class="skill-row__name">
                {{ pickLocalized(skill, "name", locale) }}
              </strong>
              <ul v-if="skill.technologies.length" class="skill-tech">
                <li
                  v-for="tech in skill.technologies"
                  :key="tech.id"
                  class="tag"
                  :class="{ 'tag--quip': quipFor(tech.name) }"
                  :data-quip="quipFor(tech.name) || null"
                  :tabindex="quipFor(tech.name) ? 0 : undefined"
                >
                  {{ tech.name }}
                </li>
              </ul>
              <div
                class="skill-rating"
                role="img"
                :aria-label="`${t('labels.level')}: ${levelLabel(skill.level)} (${skill.level} / 5)`"
              >
                <span class="skill-dots" aria-hidden="true">
                  <span
                    v-for="n in 5"
                    :key="n"
                    class="skill-dot"
                    :class="{ 'skill-dot--filled': n <= skill.level }"
                  />
                </span>
                <span class="skill-level-label">
                  {{ levelLabel(skill.level) }}
                </span>
              </div>
            </li>
          </ul>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.tag--quip {
  position: relative;
  cursor: help;
}

.tag--quip::after {
  content: attr(data-quip);
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background: var(--color-fg, #111);
  color: var(--color-surface, #fff);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  line-height: 1.3;
  width: max-content;
  max-width: 240px;
  white-space: normal;
  text-align: center;
  opacity: 0;
  pointer-events: none;
  transition:
    opacity 140ms,
    transform 140ms;
  z-index: 20;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
}

.tag--quip:hover::after,
.tag--quip:focus-visible::after {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
</style>
