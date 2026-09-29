import { watch } from "vue";
import { storeToRefs } from "pinia";
import { useThemeStore } from "@/stores/theme";
import { packFor } from "@/themes/registry";

const DEFAULT_FAVICON = "/app-icon.png";
const DEFAULT_TYPE = "image/png";

function mimeFor(href: string): string {
  return href.endsWith(".svg") ? "image/svg+xml" : DEFAULT_TYPE;
}

/**
 * Swaps the browser-tab favicon for themes that declare a `favicon` in their
 * `ThemePack` (e.g. Comic Mode's bolt badge); falls back to the default
 * `/app-icon.png` for every other theme.
 */
export function useFavicon(): void {
  const { theme } = storeToRefs(useThemeStore());

  watch(
    theme,
    (value) => {
      if (typeof document === "undefined") return;
      const href = packFor(value)?.favicon ?? DEFAULT_FAVICON;
      let link = document.querySelector<HTMLLinkElement>('link[rel="icon"]');
      if (!link) {
        link = document.createElement("link");
        link.rel = "icon";
        document.head.appendChild(link);
      }
      link.type = mimeFor(href);
      link.href = href;
    },
    { immediate: true },
  );
}
