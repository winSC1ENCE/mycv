import { useRoute, useRouter } from "vue-router";
import { storeAccessKey } from "@/api/client";
import { useCvStore } from "@/stores/cv";

export function useAccessKey(): void {
  const route = useRoute();
  const router = useRouter();
  const cvStore = useCvStore();

  const incoming = route.query.key;
  if (typeof incoming === "string" && incoming.length > 0) {
    storeAccessKey(incoming);
    const rest = Object.fromEntries(Object.entries(route.query).filter(([k]) => k !== "key"));
    router.replace({ query: rest });
    cvStore.load();
  }
}
