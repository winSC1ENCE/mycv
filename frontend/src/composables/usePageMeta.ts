import { useHead } from "@unhead/vue";
import { computed, type ComputedRef } from "vue";

type Source<T> = T | ComputedRef<T> | (() => T);

interface PageMetaOptions {
  title: Source<string>;
  description: Source<string>;
  jsonLd?: () => Record<string, unknown>;
  image?: string;
}

function toValue<T>(s: Source<T>): T {
  if (typeof s === "function") return (s as () => T)();
  if (s && typeof s === "object" && "value" in (s as object)) {
    return (s as ComputedRef<T>).value;
  }
  return s as T;
}

/**
 * Inject SEO/OG meta tags and (optionally) a JSON-LD script for the current view.
 * All inputs are reactive — useHead re-evaluates them when reactive deps change.
 */
export function usePageMeta(opts: PageMetaOptions): void {
  const title = computed(() => toValue(opts.title));
  const description = computed(() => toValue(opts.description));
  const ogImage = opts.image ?? "/og-image.png";

  useHead({
    title,
    meta: [
      { name: "description", content: description },
      { property: "og:title", content: title },
      { property: "og:description", content: description },
      { property: "og:type", content: "profile" },
      { property: "og:image", content: ogImage },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: title },
      { name: "twitter:description", content: description },
    ],
    script: opts.jsonLd
      ? [
          {
            type: "application/ld+json",
            innerHTML: computed(() => JSON.stringify(opts.jsonLd!())),
          },
        ]
      : [],
  });
}
