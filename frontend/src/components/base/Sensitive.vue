<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { computed } from "vue";
import Icon from "@/components/base/Icon.vue";

const props = withDefaults(
  defineProps<{
    blurred: boolean;
    tooltip?: string;
  }>(),
  { tooltip: undefined },
);

const { t } = useI18n();
const resolvedTooltip = computed(() => props.tooltip ?? t("sensitive.tooltip"));
</script>

<template>
  <span class="sensitive" :class="{ 'sensitive--blurred': blurred }">
    <span class="sensitive__text"><slot /></span>
    <span
      v-if="blurred"
      class="sensitive__chip"
      :data-tooltip="resolvedTooltip"
      :aria-label="t('sensitive.ariaLabel')"
      tabindex="0"
    >
      <Icon name="lock" :size="11" />
    </span>
  </span>
</template>

<style scoped>
.sensitive {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.sensitive--blurred .sensitive__text {
  filter: blur(4px) saturate(0.85);
  user-select: none;
  letter-spacing: 0.08em;
  transition: filter 150ms ease;
}

.sensitive__chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: var(--color-accent-soft, rgba(99, 102, 241, 0.12));
  color: var(--color-accent, #6366f1);
  border-radius: 999px;
  cursor: help;
  position: relative;
  transition: background-color 120ms;
}

.sensitive__chip:hover,
.sensitive__chip:focus-visible {
  background: var(--color-accent);
  color: var(--color-surface, #fff);
  outline: none;
}

.sensitive__chip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background: var(--color-fg, #111);
  color: var(--color-surface, #fff);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition:
    opacity 140ms,
    transform 140ms;
  z-index: 10;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
}

.sensitive__chip::before {
  content: "";
  position: absolute;
  bottom: calc(100% + 2px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  border: 4px solid transparent;
  border-top-color: var(--color-fg, #111);
  opacity: 0;
  pointer-events: none;
  transition:
    opacity 140ms,
    transform 140ms;
  z-index: 10;
}

.sensitive__chip:hover::after,
.sensitive__chip:focus-visible::after,
.sensitive__chip:hover::before,
.sensitive__chip:focus-visible::before {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

[data-theme="dog"] .sensitive--blurred .sensitive__text {
  filter: none;
  background: repeating-linear-gradient(
    90deg,
    var(--color-fg) 0 10px,
    transparent 10px 14px
  );
  color: transparent;
  border-radius: 2px;
}

[data-theme="dog"] .sensitive__chip {
  background: var(--color-fg);
  color: var(--color-surface);
  border-radius: 0;
  transform: rotate(-3deg);
  border: 2px solid var(--color-fg);
}

[data-theme="dog"] .sensitive__chip::after {
  border-radius: 0;
  font-family: var(--font-display, inherit);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border: 2px solid var(--color-surface);
}
</style>
