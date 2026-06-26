<script setup lang="ts">
import { computed, ref } from "vue";
import { packFor } from "@/themes/registry";
import EasterEggModal from "./EasterEggModal.vue";

const props = defineProps<{ theme: string }>();

const egg = computed(() => packFor(props.theme)?.easterEgg ?? null);
const open = ref(false);
</script>

<template>
  <template v-if="egg">
    <button
      type="button"
      class="easter-egg-fab"
      :aria-label="$t(egg.buttonKey)"
      @click="open = true"
    >
      {{ $t(egg.buttonKey) }}
    </button>
    <EasterEggModal v-model:open="open" :egg="egg" />
  </template>
</template>

<style scoped>
.easter-egg-fab {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 900;
  padding: 12px 18px;
  border-radius: 999px;
  border: 2px solid var(--color-fg, #0a0a0a);
  background: var(--color-surface, #fff);
  color: var(--color-fg, #0a0a0a);
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
  transition:
    transform 120ms ease,
    box-shadow 120ms ease;
}

.easter-egg-fab:hover,
.easter-egg-fab:focus-visible {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.28);
  outline: none;
}

@media (max-width: 480px) {
  .easter-egg-fab {
    right: 12px;
    bottom: 12px;
    font-size: 0.85rem;
    padding: 10px 14px;
  }
}
</style>
