<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { computed } from "vue";

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
  <span
    class="sensitive"
    :class="{ 'sensitive--blurred': blurred }"
    :title="blurred ? resolvedTooltip : undefined"
    :aria-label="blurred ? t('sensitive.ariaLabel') : undefined"
  ><slot /></span>
</template>
