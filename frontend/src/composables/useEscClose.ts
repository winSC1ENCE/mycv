import { onMounted, onUnmounted, type Ref } from "vue";

/**
 * Closes an edit/add modal when the user presses Esc.
 *
 * @param closeFn  what to do when Esc is pressed (typically `editing.value = null`)
 * @param enabled  reactive flag; the listener only acts when this is true
 */
export function useEscClose(closeFn: () => void, enabled: Ref<boolean>): void {
  function onKeydown(e: KeyboardEvent): void {
    if (e.key === "Escape" && enabled.value) {
      closeFn();
    }
  }
  onMounted(() => window.addEventListener("keydown", onKeydown));
  onUnmounted(() => window.removeEventListener("keydown", onKeydown));
}
