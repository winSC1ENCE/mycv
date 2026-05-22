<template>
  <div class="file-upload">
    <label class="file-upload__label">
      <input
        ref="inputRef"
        class="file-upload__input"
        type="file"
        :accept="accept"
        @change="onFileSelected"
      />
      <span class="file-upload__trigger">
        {{ $t("admin.chooseFile") }}
      </span>
    </label>

    <p v-if="error" class="file-upload__error">{{ error }}</p>
    <p v-if="uploading" class="file-upload__status">{{ $t("common.loading") }}…</p>

    <!-- Image crop modal -->
    <div v-if="cropSrc" class="crop-modal">
      <div class="crop-modal__inner">
        <Cropper
          ref="cropperRef"
          class="crop-modal__cropper"
          :src="cropSrc"
          :stencil-props="{ aspectRatio: 0 }"
        />
        <div class="crop-modal__actions">
          <button type="button" class="btn btn--primary" @click="confirmCrop">
            {{ $t("admin.crop") }}
          </button>
          <button type="button" class="btn" @click="cancelCrop">
            {{ $t("admin.cancel") }}
          </button>
        </div>
      </div>
    </div>

    <!-- Non-image preview -->
    <div v-if="nonImageFile" class="file-upload__preview">
      📄 {{ nonImageFile.name }} ({{ (nonImageFile.size / 1024).toFixed(1) }} KB)
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Cropper } from "vue-advanced-cropper";
import "vue-advanced-cropper/dist/style.css";
import { uploadMedia } from "@/api/admin";
import type { MediaAsset } from "@/api/types";

const MAX_SIZE_BYTES = 5 * 1024 * 1024;

withDefaults(defineProps<{ accept?: string }>(), { accept: "image/*,application/pdf" });
const emit = defineEmits<{ uploaded: [asset: MediaAsset] }>();

const inputRef = ref<HTMLInputElement | null>(null);
const cropperRef = ref<InstanceType<typeof Cropper> | null>(null);
const cropSrc = ref<string | null>(null);
const nonImageFile = ref<File | null>(null);
const uploading = ref(false);
const error = ref<string | null>(null);
let pendingFile: File | null = null;

function onFileSelected(e: Event): void {
  error.value = null;
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;

  if (file.size > MAX_SIZE_BYTES) {
    error.value = `File too large (max 5 MB).`;
    return;
  }

  if (file.type.startsWith("image/")) {
    pendingFile = file;
    const reader = new FileReader();
    reader.onload = (ev) => {
      cropSrc.value = ev.target?.result as string;
    };
    reader.readAsDataURL(file);
  } else {
    nonImageFile.value = file;
    doUpload(file);
  }
}

async function confirmCrop(): Promise<void> {
  if (!cropperRef.value || !pendingFile) return;
  const { canvas } = cropperRef.value.getResult();
  canvas?.toBlob(async (blob) => {
    if (!blob) return;
    const croppedFile = new File([blob], pendingFile!.name, { type: pendingFile!.type });
    cropSrc.value = null;
    await doUpload(croppedFile);
  }, pendingFile.type);
}

function cancelCrop(): void {
  cropSrc.value = null;
  pendingFile = null;
  if (inputRef.value) inputRef.value.value = "";
}

async function doUpload(file: File): Promise<void> {
  uploading.value = true;
  error.value = null;
  try {
    const asset = await uploadMedia(file);
    emit("uploaded", asset);
    nonImageFile.value = null;
  } catch {
    error.value = "Upload failed. Please try again.";
  } finally {
    uploading.value = false;
  }
}
</script>

<style scoped>
.file-upload {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.file-upload__input {
  display: none;
}

.file-upload__trigger {
  display: inline-block;
  padding: var(--space-2) var(--space-4);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-fg-muted);
  transition: border-color 0.15s;
}

.file-upload__trigger:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.file-upload__error {
  font-size: 0.75rem;
  color: var(--color-error, #dc2626);
}

.file-upload__status {
  font-size: 0.875rem;
  color: var(--color-fg-muted);
}

.file-upload__preview {
  font-size: 0.875rem;
  color: var(--color-fg-muted);
}

.crop-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.crop-modal__inner {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 90vw;
  max-height: 90vh;
}

.crop-modal__cropper {
  width: 600px;
  max-width: 80vw;
  height: 400px;
  max-height: 60vh;
}

.crop-modal__actions {
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}

.btn {
  padding: var(--space-2) var(--space-5);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.9rem;
  background: var(--color-surface);
  color: var(--color-fg);
}

.btn--primary {
  background: var(--color-accent);
  color: #fff;
  border-color: var(--color-accent);
}
</style>
