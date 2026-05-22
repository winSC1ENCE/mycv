import { afterEach, describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import ImageLightbox from "@/components/base/ImageLightbox.vue";
import type { MediaAsset } from "@/api/types";

const i18n = createI18n({
  legacy: false,
  locale: "en",
  messages: {
    en: {
      actions: {
        close: "Close",
        previous: "Previous",
        next: "Next",
      },
    },
  },
});

function makeImage(id: number, url = `https://example.com/${id}.jpg`): MediaAsset {
  return {
    id,
    url,
    alt_text: `Image ${id}`,
    kind: "image",
    order: id,
  };
}

function mountLightbox(props: {
  images: MediaAsset[];
  open: boolean;
  initialIndex?: number;
}) {
  return mount(ImageLightbox, {
    global: { plugins: [i18n] },
    props,
    attachTo: document.body,
  });
}

afterEach(() => {
  document.body.innerHTML = "";
});

describe("ImageLightbox.vue", () => {
  it("renders nothing in the DOM when open=false", () => {
    mountLightbox({ images: [makeImage(1)], open: false });
    expect(document.body.querySelector(".image-lightbox")).toBeNull();
  });

  it("renders the image at initialIndex when open=true", () => {
    mountLightbox({
      images: [makeImage(1), makeImage(2), makeImage(3)],
      open: true,
      initialIndex: 1,
    });
    const img = document.body.querySelector(".image-lightbox__img") as HTMLImageElement | null;
    expect(img).not.toBeNull();
    expect(img!.getAttribute("src")).toBe("https://example.com/2.jpg");
  });

  it("emits update:open=false when the ✕ button is clicked", async () => {
    const wrapper = mountLightbox({ images: [makeImage(1)], open: true });
    const close = document.body.querySelector(".image-lightbox__close") as HTMLButtonElement;
    close.click();
    await wrapper.vm.$nextTick();
    expect(wrapper.emitted("update:open")).toBeTruthy();
    expect(wrapper.emitted("update:open")![0]).toEqual([false]);
  });

  it("emits update:open=false when the backdrop is clicked", async () => {
    const wrapper = mountLightbox({ images: [makeImage(1)], open: true });
    const backdrop = document.body.querySelector(".image-lightbox") as HTMLElement;
    backdrop.dispatchEvent(
      new MouseEvent("click", { bubbles: true, cancelable: true }),
    );
    await wrapper.vm.$nextTick();
    expect(wrapper.emitted("update:open")).toBeTruthy();
  });

  it("emits update:open=false when Escape is pressed", async () => {
    const wrapper = mountLightbox({ images: [makeImage(1)], open: true });
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await wrapper.vm.$nextTick();
    expect(wrapper.emitted("update:open")).toBeTruthy();
    expect(wrapper.emitted("update:open")![0]).toEqual([false]);
  });

  it("hides prev/next when there is only one image", () => {
    mountLightbox({ images: [makeImage(1)], open: true });
    expect(document.body.querySelector(".image-lightbox__nav--prev")).toBeNull();
    expect(document.body.querySelector(".image-lightbox__nav--next")).toBeNull();
  });

  it("shows prev/next when there are multiple images", () => {
    mountLightbox({ images: [makeImage(1), makeImage(2)], open: true });
    expect(document.body.querySelector(".image-lightbox__nav--prev")).not.toBeNull();
    expect(document.body.querySelector(".image-lightbox__nav--next")).not.toBeNull();
  });

  it("ArrowRight cycles to the next image (modulo N)", async () => {
    const wrapper = mountLightbox({
      images: [makeImage(1), makeImage(2), makeImage(3)],
      open: true,
      initialIndex: 0,
    });
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight" }));
    await wrapper.vm.$nextTick();
    const img = document.body.querySelector(".image-lightbox__img") as HTMLImageElement;
    expect(img.getAttribute("src")).toBe("https://example.com/2.jpg");
  });

  it("ArrowLeft wraps around to the last image when at index 0", async () => {
    const wrapper = mountLightbox({
      images: [makeImage(1), makeImage(2), makeImage(3)],
      open: true,
      initialIndex: 0,
    });
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowLeft" }));
    await wrapper.vm.$nextTick();
    const img = document.body.querySelector(".image-lightbox__img") as HTMLImageElement;
    expect(img.getAttribute("src")).toBe("https://example.com/3.jpg");
  });

  it("does not react to keys when closed", async () => {
    const wrapper = mountLightbox({ images: [makeImage(1)], open: false });
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await wrapper.vm.$nextTick();
    expect(wrapper.emitted("update:open")).toBeUndefined();
  });
});
