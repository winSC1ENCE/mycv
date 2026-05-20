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
    },
  },
});

function mountPreview(media: MediaAsset, alt = "") {
  return mount(MediaPreview, {
    global: { plugins: [i18n] },
    props: { media, alt },
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
  it("renders <img> when kind=image with url", () => {
    const wrapper = mountPreview(makeAsset({ kind: "image" }));
    const img = wrapper.find("img");
    expect(img.exists()).toBe(true);
    expect(img.attributes("src")).toBe("https://example.com/file.jpg");
    expect(img.attributes("alt")).toBe("Example file");
  });

  it("renders <iframe> when kind=document with url", () => {
    const wrapper = mountPreview(
      makeAsset({ kind: "document", url: "https://example.com/file.pdf" }),
    );
    const iframe = wrapper.find("iframe");
    expect(iframe.exists()).toBe(true);
    expect(iframe.attributes("src")).toBe("https://example.com/file.pdf");
  });

  it("renders <video> when kind=video with url", () => {
    const wrapper = mountPreview(
      makeAsset({ kind: "video", url: "https://example.com/file.mp4" }),
    );
    const video = wrapper.find("video");
    expect(video.exists()).toBe(true);
    expect(video.attributes("src")).toBe("https://example.com/file.mp4");
    expect(video.attributes("controls")).toBeDefined();
  });

  it("renders locked placeholder when url is empty", () => {
    const wrapper = mountPreview(makeAsset({ url: "", kind: "image" }));
    expect(wrapper.find("img").exists()).toBe(false);
    expect(wrapper.find("iframe").exists()).toBe(false);
    const locked = wrapper.find(".media-preview__locked");
    expect(locked.exists()).toBe(true);
    expect(locked.attributes("aria-label")).toBe("Locked file");
    expect(locked.attributes("title")).toBe("Order access via cv@chlous.top");
  });

  it("falls back to alt prop when alt_text is empty", () => {
    const wrapper = mountPreview(makeAsset({ alt_text: "", kind: "image" }), "Fallback alt");
    expect(wrapper.find("img").attributes("alt")).toBe("Fallback alt");
  });
});
