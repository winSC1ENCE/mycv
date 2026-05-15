<template>
  <VueDraggable v-model="localItems" handle=".drag-handle" item-key="id" @end="onEnd">
    <template #item="{ element }">
      <slot name="item" :item="element" />
    </template>
  </VueDraggable>
</template>

<script setup lang="ts" generic="T extends { id: number }">
import { ref, watch } from "vue";
import { VueDraggable } from "vue-draggable-plus";

const props = defineProps<{ items: T[] }>();
const emit = defineEmits<{ reorder: [ids: number[]] }>();

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const localItems = ref([...props.items]) as any;

watch(
  () => props.items,
  (next: T[]) => {
    localItems.value = [...next];
  },
);

function onEnd(): void {
  emit(
    "reorder",
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (localItems.value as any[]).map((item: T) => item.id),
  );
}
</script>
