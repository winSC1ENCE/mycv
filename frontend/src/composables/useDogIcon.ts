/**
 * Deterministic random-feeling icon picker for the Dog Mode timeline nodes.
 *
 * Given a stable per-row uid (e.g. "experience-10"), returns one of the
 * dog-themed PNGs in /icons/dog/. Same uid → same icon across reloads; new
 * admin entries get a fresh pick by virtue of having a new id.
 */

export const DOG_ICONS = [
  "/icons/dog/paws.png",
  "/icons/dog/dog-face.png",
  "/icons/dog/dog-skateboard.png",
  "/icons/dog/dog-sitting.png",
  "/icons/dog/dog-sleeping.png",
  "/icons/dog/ball.png",
  "/icons/dog/doghouse.png",
  "/icons/dog/bone.png",
  "/icons/dog/rope-toy.png",
  "/icons/dog/bowl.png",
] as const;

export function dogIconFor(uid: string): string {
  const h = Array.from(uid).reduce((a, c) => a + c.charCodeAt(0), 0);
  return DOG_ICONS[h % DOG_ICONS.length];
}
