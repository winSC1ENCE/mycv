import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import MediaPreview from "@/components/base/MediaPreview.vue";
import type { MediaAsset } from "@/api/types";

const i18n = createI18n({
  legacy: false,
  locale: "en",
  messages: {
    en: {
      sensitive: { tooltip: "Order access via cv{'@'}chlous.top" },
      timeline: { locked_file: "Locked file" },
      actions: {
        openPdf: "Open PDF",
        zoom_image: "Zoom image",
        close: "Close",
        previous: "Previous",
        next: "Next",
      },
    },
  },
});

function mountPreview(media: MediaAsset, alt = "") {
  return mount(MediaPreview, {
    global: { plugins: [i18n] },
    props: { media, alt },
    attachTo: document.body,
  });
}

function makeAsset(overrides: Partial<MediaAsset>): MediaAsset {
  return {
    id: 1,
    url: "https://example.com/file.jpg",
    alt_text: "Example file",
    kind: "image",
    order: 0,
    ...overrides,
  };
}

describe("MediaPreview.vue", () => {
  it("renders an <img> inside a clickable button when kind=image", () => {
    const wrapper = mountPreview(makeAsset({ kind: "image" }));
    const button = wrapper.find("button.media-preview__img-btn");
    expect(button.exists()).toBe(true);
    const img = button.find("img");
    expect(img.exists()).toBe(true);
    expect(img.attributes("src")).toBe("https://example.com/file.jpg");
    expect(img.attributes("alt")).toBe("Example file");
    wrapper.unmount();
  });

  it("opens the lightbox when the image button is clicked", async () => {
    const wrapper = mountPreview(makeAsset({ kind: "image" }));
    expect(document.body.querySelector(".image-lightbox")).toBeNull();
    await wrapper.find("button.media-preview__img-btn").trigger("click");
    expect(document.body.querySelector(".image-lightbox")).not.toBeNull();
    wrapper.unmount();
  });

  it("renders a PDF card (icon + title + Open PDF link) when kind=document", () => {
    const wrapper = mountPreview(
      makeAsset({
        kind: "document",
        url: "https://example.com/file.pdf",
        alt_text: "My Certificate",
      }),
    );
    expect(wrapper.find("embed").exists()).toBe(false);
    const card = wrapper.find(".media-preview__pdf-card");
    expect(card.exists()).toBe(true);
    expect(card.find("svg[data-icon='file-text']").exists()).toBe(true);
    expect(card.find(".media-preview__pdf-title").text()).toBe("My Certificate");
    const link = card.find("a.media-preview__pdf-button");
    expect(link.attributes("href")).toBe("https://example.com/file.pdf");
    expect(link.attributes("target")).toBe("_blank");
    expect(link.text()).toBe("Open PDF");
    wrapper.unmount();
  });

  it("PDF card falls back to alt prop when alt_text is empty", () => {
    const wrapper = mountPreview(
      makeAsset({ kind: "document", alt_text: "", url: "/file.pdf" }),
      "Fallback title",
    );
    expect(wrapper.find(".media-preview__pdf-title").text()).toBe("Fallback title");
    wrapper.unmount();
  });

  it("renders <video> when kind=video with url", () => {
    const wrapper = mountPreview(makeAsset({ kind: "video", url: "https://example.com/file.mp4" }));
    const video = wrapper.find("video");
    expect(video.exists()).toBe(true);
    expect(video.attributes("src")).toBe("https://example.com/file.mp4");
    expect(video.attributes("controls")).toBeDefined();
    wrapper.unmount();
  });

  it("renders locked placeholder with Icon when url is empty", () => {
    const wrapper = mountPreview(makeAsset({ url: "", kind: "image" }));
    expect(wrapper.find("img").exists()).toBe(false);
    expect(wrapper.find("embed").exists()).toBe(false);
    const locked = wrapper.find(".media-preview__locked");
    expect(locked.exists()).toBe(true);
    expect(locked.attributes("aria-label")).toBe("Locked file");
    expect(locked.attributes("data-tooltip")).toBe("Order access via cv@chlous.top");
    expect(locked.find("svg[data-icon='lock']").exists()).toBe(true);
    wrapper.unmount();
  });

  it("falls back to alt prop when alt_text is empty (image)", () => {
    const wrapper = mountPreview(makeAsset({ alt_text: "", kind: "image" }), "Fallback alt");
    expect(wrapper.find("img").attributes("alt")).toBe("Fallback alt");
    wrapper.unmount();
  });
});
