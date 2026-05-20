import { useRouter } from "vue-router";
import { storeAccessKey } from "@/api/client";
import { useCvStore } from "@/stores/cv";

export function useAccessKey(): void {
  const router = useRouter();
  const cvStore = useCvStore();

  // Read directly from window.location — Vue Router's reactive route may not be resolved
  // yet during initial setup, but URLSearchParams is always synchronously available.
  const params = new URLSearchParams(window.location.search);
  const incoming = params.get("key");

  if (incoming && incoming.length > 0) {
    storeAccessKey(incoming);
    cvStore.load();
    // Strip the key from the URL once the router is ready (cosmetic; localStorage already has it).
    router.isReady().then(() => {
      params.delete("key");
      const query = Object.fromEntries(params.entries());
      router.replace({ query });
    });
  }
}
