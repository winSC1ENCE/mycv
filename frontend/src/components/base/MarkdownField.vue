<script setup lang="ts">
import { ref } from "vue";
import RichText from "@/components/base/RichText.vue";

const props = withDefaults(defineProps<{ modelValue?: string; rows?: number }>(), {
  modelValue: "",
  rows: 3,
});
const emit = defineEmits<{ "update:modelValue": [value: string] }>();

const textarea = ref<HTMLTextAreaElement | null>(null);
const preview = ref(false);

type Wrap = { before: string; after: string; placeholder: string };

function applyWrap({ before, after, placeholder }: Wrap): void {
  const el = textarea.value;
  if (!el) return;
  const start = el.selectionStart;
  const end = el.selectionEnd;
  const value = props.modelValue;
  const selected = value.slice(start, end) || placeholder;
  const next = value.slice(0, start) + before + selected + after + value.slice(end);
  emit("update:modelValue", next);
  void Promise.resolve().then(() => {
    el.focus();
    el.selectionStart = start + before.length;
    el.selectionEnd = start + before.length + selected.length;
  });
}

function applyList(): void {
  const el = textarea.value;
  if (!el) return;
  const start = el.selectionStart;
  const value = props.modelValue;
  const lineStart = value.lastIndexOf("\n", start - 1) + 1;
  const next = value.slice(0, lineStart) + "- " + value.slice(lineStart);
  emit("update:modelValue", next);
  void Promise.resolve().then(() => {
    el.focus();
    el.selectionStart = el.selectionEnd = start + 2;
  });
}

function onInput(event: Event): void {
  emit("update:modelValue", (event.target as HTMLTextAreaElement).value);
}
</script>

<template>
  <div class="md-field">
    <div class="md-field__toolbar">
      <button
        type="button"
        class="md-field__btn"
        title="Bold"
        :disabled="preview"
        @click="applyWrap({ before: '**', after: '**', placeholder: 'bold' })"
      >
        <strong>B</strong>
      </button>
      <button
        type="button"
        class="md-field__btn"
        title="Italic"
        :disabled="preview"
        @click="applyWrap({ before: '_', after: '_', placeholder: 'italic' })"
      >
        <em>I</em>
      </button>
      <button
        type="button"
        class="md-field__btn"
        title="Bullet list"
        :disabled="preview"
        @click="applyList"
      >
        ☰
      </button>
      <button
        type="button"
        class="md-field__btn"
        title="Link"
        :disabled="preview"
        @click="applyWrap({ before: '[', after: '](https://)', placeholder: 'text' })"
      >
        🔗
      </button>
      <button
        type="button"
        class="md-field__toggle"
        :class="{ 'md-field__toggle--active': preview }"
        @click="preview = !preview"
      >
        {{ preview ? "Write" : "Preview" }}
      </button>
    </div>

    <RichText v-if="preview" :text="modelValue" class="md-field__preview" />
    <textarea
      v-else
      ref="textarea"
      :value="modelValue"
      :rows="rows"
      class="md-field__input"
      @input="onInput"
    ></textarea>
  </div>
</template>

<style scoped>
.md-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.md-field__toolbar {
  display: flex;
  gap: var(--space-1);
  align-items: center;
}

.md-field__btn,
.md-field__toggle {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  cursor: pointer;
  font-size: 0.85rem;
  line-height: 1.4;
}

.md-field__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.md-field__toggle {
  margin-left: auto;
}

.md-field__toggle--active {
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.md-field__preview {
  min-height: 4rem;
  padding: var(--space-2);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
}
</style>
