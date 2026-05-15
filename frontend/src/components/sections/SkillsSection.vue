<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import type { SkillCategory } from "@/api/types";

defineProps<{ categories: SkillCategory[] }>();
const { locale } = storeToRefs(useLocaleStore());
</script>

<template>
  <section class="section" aria-labelledby="skills-title">
    <div class="container">
      <h2 id="skills-title" class="section__title">{{ $t("nav.skills") }}</h2>
      <div class="grid grid--2">
        <article v-for="cat in categories" :key="cat.id" class="card">
          <h3>{{ pickLocalized(cat, "name", locale) }}</h3>
          <ul style="list-style: none; padding: 0; margin: 0">
            <li v-for="skill in cat.skills" :key="skill.id" style="margin-bottom: var(--space-3)">
              <strong>{{ pickLocalized(skill, "name", locale) }}</strong>
              <div class="skill-bar" :aria-label="`${$t('labels.level')} ${skill.level} / 5`">
                <div class="skill-bar__fill" :style="{ width: `${(skill.level / 5) * 100}%` }" />
              </div>
              <div>
                <span v-for="tech in skill.technologies" :key="tech.id" class="tag">{{
                  tech.name
                }}</span>
              </div>
            </li>
          </ul>
        </article>
      </div>
    </div>
  </section>
</template>
