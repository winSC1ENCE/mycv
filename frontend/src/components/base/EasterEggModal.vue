<script setup lang="ts">
import { computed } from "vue";
import { useEscClose } from "@/composables/useEscClose";
import type { EasterEggConfig } from "@/themes/types";

const props = defineProps<{ open: boolean; egg: EasterEggConfig }>();
const emit = defineEmits<{ "update:open": [value: boolean] }>();

function close(): void {
  emit("update:open", false);
}

useEscClose(
  close,
  computed(() => props.open),
);
</script>

<template>
  <Teleport to="body">
    <Transition name="egg-fade">
      <div v-if="open" class="egg-overlay" @click.self="close">
        <div class="egg-modal" role="dialog" aria-modal="true" :aria-label="$t(egg.titleKey)">
          <button
            type="button"
            class="egg-modal__close"
            :aria-label="$t('actions.close')"
            @click="close"
          >
            ✕
          </button>
          <h2 class="egg-modal__title">{{ $t(egg.titleKey) }}</h2>
          <p class="egg-modal__intro">{{ $t(egg.introKey) }}</p>
          <table class="egg-table">
            <thead>
              <tr>
                <th></th>
                <th>{{ $t(egg.valueHeadKey) }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in egg.rows" :key="row.labelKey">
                <td>{{ $t(row.labelKey) }}</td>
                <td class="egg-table__value">{{ row.value }}</td>
              </tr>
            </tbody>
          </table>
          <p class="egg-modal__footnote">{{ $t(egg.footnoteKey) }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.egg-overlay {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background: rgba(0, 0, 0, 0.6);
}

.egg-modal {
  position: relative;
  width: min(440px, 100%);
  background: var(--color-surface, #fff);
  color: var(--color-fg, #0a0a0a);
  border: 2px solid var(--color-fg, #0a0a0a);
  border-radius: 12px;
  padding: var(--space-5) var(--space-4) var(--space-4);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
  font-family: var(--font-mono, monospace);
}

.egg-modal__close {
  position: absolute;
  top: 10px;
  right: 12px;
  border: none;
  background: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--color-fg-muted, #555);
}

.egg-modal__title {
  margin: 0 0 var(--space-3);
  font-size: 1.1rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.egg-modal__intro {
  margin: 0 0 var(--space-3);
  font-size: 0.9rem;
}

.egg-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--space-3);
}

.egg-table th,
.egg-table td {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--color-border, #ddd);
}

.egg-table th {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-fg-muted, #555);
}

.egg-table__value {
  text-align: right;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.egg-modal__footnote {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 700;
}

.egg-fade-enter-active,
.egg-fade-leave-active {
  transition: opacity 160ms ease;
}

.egg-fade-enter-from,
.egg-fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .egg-fade-enter-active,
  .egg-fade-leave-active {
    transition: none;
  }
}
</style>
