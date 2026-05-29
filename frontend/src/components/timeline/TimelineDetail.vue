<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useLocaleStore } from "@/stores/locale";
import { useI18n } from "vue-i18n";
import { pickLocalized } from "@/composables/useLocalized";
import { formatDate } from "@/utils/dateFormat";
import MediaPreview from "@/components/base/MediaPreview.vue";
import RichText from "@/components/base/RichText.vue";
import type { TimelineRow } from "@/stores/cv";

defineProps<{ row: TimelineRow }>();
const { locale } = storeToRefs(useLocaleStore());
const { t } = useI18n();

function fmt(iso: string): string {
  return formatDate(iso, locale.value);
}
</script>

<template>
  <div class="timeline-detail">
    <template v-if="row.kind === 'experience'">
      <p class="timeline-detail__dates">
        {{ fmt(row.data.start_date) }} →
        {{ row.data.end_date ? fmt(row.data.end_date) : t("labels.present") }}
        <span v-if="row.data.location"> · {{ row.data.location }}</span>
      </p>
      <RichText
        v-if="pickLocalized(row.data, 'description', locale)"
        :text="pickLocalized(row.data, 'description', locale)"
        class="timeline-detail__body"
      />
      <ul v-if="row.data.technologies.length" class="timeline-detail__tags">
        <li v-for="tech in row.data.technologies" :key="tech.id" class="tag">{{ tech.name }}</li>
      </ul>
      <MediaPreview
        v-if="row.data.media"
        :media="row.data.media"
        :alt="pickLocalized(row.data, 'role', locale)"
      />
      <div v-if="row.certs.length" class="timeline-detail__certs">
        <h4>{{ t("timeline.linked_certificates") }}</h4>
        <ul>
          <li v-for="cert in row.certs" :key="cert.id">
            <strong>{{ pickLocalized(cert, "name", locale) }}</strong>
            <span class="timeline-detail__cert-meta">
              · {{ cert.issuer }} · {{ fmt(cert.issue_date) }}</span
            >
          </li>
        </ul>
      </div>
    </template>

    <template v-else-if="row.kind === 'education'">
      <p class="timeline-detail__dates">
        {{ fmt(row.data.start_date) }} →
        {{ row.data.end_date ? fmt(row.data.end_date) : t("labels.present") }}
        <span v-if="row.data.location"> · {{ row.data.location }}</span>
      </p>
      <RichText
        v-if="pickLocalized(row.data, 'description', locale)"
        :text="pickLocalized(row.data, 'description', locale)"
        class="timeline-detail__body"
      />
      <ul v-if="row.data.technologies.length" class="timeline-detail__tags">
        <li v-for="tech in row.data.technologies" :key="tech.id" class="tag">{{ tech.name }}</li>
      </ul>
      <div v-if="row.certs.length" class="timeline-detail__certs">
        <h4>{{ t("timeline.linked_certificates") }}</h4>
        <ul>
          <li v-for="cert in row.certs" :key="cert.id">
            <strong>{{ pickLocalized(cert, "name", locale) }}</strong>
            <span class="timeline-detail__cert-meta">
              · {{ cert.issuer }} · {{ fmt(cert.issue_date) }}</span
            >
          </li>
        </ul>
      </div>
    </template>

    <template v-else-if="row.kind === 'certificate'">
      <p class="timeline-detail__dates">{{ row.data.issuer }} · {{ fmt(row.data.issue_date) }}</p>
      <RichText
        v-if="pickLocalized(row.data, 'description', locale)"
        :text="pickLocalized(row.data, 'description', locale)"
        class="timeline-detail__body"
      />
      <ul v-if="row.data.technologies.length" class="timeline-detail__tags">
        <li v-for="tech in row.data.technologies" :key="tech.id" class="tag">{{ tech.name }}</li>
      </ul>
      <MediaPreview
        v-if="row.data.media"
        :media="row.data.media"
        :alt="pickLocalized(row.data, 'name', locale)"
      />
    </template>

    <template v-else>
      <p class="timeline-detail__dates">
        <span class="kind-badge">{{ row.data.kind }}</span> · {{ fmt(row.data.date) }}
      </p>
      <RichText
        v-if="pickLocalized(row.data, 'description', locale)"
        :text="pickLocalized(row.data, 'description', locale)"
        class="timeline-detail__body"
      />
    </template>
  </div>
</template>

<style scoped>
.timeline-detail {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding-top: var(--space-3);
}

.timeline-detail__dates {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--color-muted);
  margin: 0;
}

.timeline-detail__body {
  margin: 0;
  line-height: 1.65;
}

.timeline-detail__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  list-style: none;
  padding: 0;
  margin: 0;
}

.timeline-detail__certs {
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-3);
}

.timeline-detail__certs h4 {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
  margin: 0 0 var(--space-2) 0;
}

.timeline-detail__certs ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.timeline-detail__cert-meta {
  color: var(--color-muted);
  font-size: 0.875rem;
}

.kind-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.08em;
}
</style>
