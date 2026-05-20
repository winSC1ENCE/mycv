<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useI18n } from "vue-i18n";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import { useLevelLabel } from "@/composables/useLevelLabel";
import type { SkillCategory } from "@/api/types";

defineProps<{ categories: SkillCategory[] }>();
const { locale } = storeToRefs(useLocaleStore());
const { t } = useI18n();
const levelLabel = useLevelLabel();
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
              <strong v-if="cat.slug === 'languages'" class="skill-row__name">
                {{ pickLocalized(skill, "name", locale) }}
              </strong>
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
                <span v-if="cat.slug === 'languages'" class="skill-level-label">
                  {{ levelLabel(skill.level) }}
                </span>
              </div>
              <ul v-if="skill.technologies.length" class="skill-tech">
                <li v-for="tech in skill.technologies" :key="tech.id" class="tag">
                  {{ tech.name }}
                </li>
              </ul>
            </li>
          </ul>
        </article>
      </div>
    </div>
  </section>
</template>
