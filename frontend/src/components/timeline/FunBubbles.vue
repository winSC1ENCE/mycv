<script setup lang="ts">
import { bubbles } from "@/composables/useFunBubbles";
</script>

<template>
  <Teleport to="body">
    <TransitionGroup name="fun-bubble" tag="div" class="fun-bubble-layer">
      <span
        v-for="b in bubbles"
        :key="b.id"
        class="fun-bubble"
        :class="b.size === 'big' ? 'fun-bubble--big' : ''"
        :style="{
          left: `${b.x}px`,
          top: `${b.y}px`,
          '--bubble-rotate': `${b.rotate}deg`,
        }"
        aria-hidden="true"
      >
        {{ b.text }}
      </span>
    </TransitionGroup>
  </Teleport>
</template>

<style>
.fun-bubble-layer {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1000;
}

.fun-bubble {
  position: fixed;
  transform: translate(-50%, -100%) rotate(var(--bubble-rotate, 0deg));
  background: #ffffff;
  color: #0a0a0a;
  border: 3px solid #0a0a0a;
  border-radius: 999px;
  padding: 8px 18px;
  font-family: "Comic Neue", "Comic Sans MS", system-ui, sans-serif;
  font-weight: 800;
  font-size: 1.15rem;
  letter-spacing: 0.02em;
  box-shadow: 4px 4px 0 #0a0a0a;
  white-space: nowrap;
  pointer-events: none;
  user-select: none;
  animation: fun-bubble-drift 1500ms cubic-bezier(0.2, 0.7, 0.3, 1) forwards;
}

.fun-bubble::after {
  content: "";
  position: absolute;
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 9px solid transparent;
  border-right: 9px solid transparent;
  border-top: 14px solid #0a0a0a;
}

.fun-bubble::before {
  content: "";
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 10px solid #ffffff;
  z-index: 1;
}

.fun-bubble--big {
  font-size: 1.75rem;
  padding: 14px 28px;
  border-width: 4px;
  box-shadow: 6px 6px 0 #0a0a0a;
  animation-duration: 2000ms;
}

@keyframes fun-bubble-drift {
  0% {
    opacity: 0;
    transform: translate(-50%, -100%) rotate(var(--bubble-rotate, 0deg)) scale(0.3);
  }
  15% {
    opacity: 1;
    transform: translate(-50%, -110%) rotate(var(--bubble-rotate, 0deg)) scale(1.1);
  }
  25% {
    transform: translate(-50%, -115%) rotate(var(--bubble-rotate, 0deg)) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -200%) rotate(var(--bubble-rotate, 0deg)) scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .fun-bubble {
    animation: fun-bubble-fade 1500ms ease forwards;
  }
  .fun-bubble--big {
    animation-duration: 2000ms;
  }
  @keyframes fun-bubble-fade {
    0% {
      opacity: 0;
    }
    10% {
      opacity: 1;
    }
    80% {
      opacity: 1;
    }
    100% {
      opacity: 0;
    }
  }
}
</style>
