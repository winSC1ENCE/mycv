/**
 * Dog Mode theme pack — 101-Dalmatians comic style.
 *
 * Data moved verbatim from the former `useDogIcon.ts` / `dogPhrases.ts` so dog
 * behavior is unchanged; only its home moved into the theme registry.
 */

import type { ThemePack } from "./types";

const DOG_ICONS = [
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

export const dogPack: ThemePack = {
  id: "dog",
  label: "Dog",
  emoji: "🐕",
  profilePhoto: "/profile-dog.png",
  counterKey: "timeline.pet_counter",
  nodeIcons: DOG_ICONS,
  phrases: {
    en: {
      iconPhrases: {
        bone: ["YUM!", "CRUNCH!", "TASTY!", "MINE!"],
        ball: ["FETCH!", "CATCH!", "ROLL!", "BOUNCE!"],
        bowl: ["NOM NOM!", "YUMMY!", "GIMME!", "SLURP!"],
        doghouse: ["HOME!", "COZY!", "SAFE!", "ZZZ…"],
        "rope-toy": ["TUG!", "PULL!", "GRRR!", "MINE!"],
        "dog-sleeping": ["Zzz…", "SNORE", "DREAM…", "SHHH…"],
        "dog-skateboard": ["WHEE!", "VROOM!", "LOOK!", "YIKES!"],
        paws: ["TAP TAP", "PAT PAT", "TROT…", "STEP STEP"],
      },
      defaultPhrases: ["WUFF!", "BARK!", "WOOF!", "BORK!", "AWOOO!"],
      praise: {
        3: "GOOD DOG!",
        7: "WHO'S A GOOD BOY?",
        15: "BEST FRIEND!",
        30: "DOG WHISPERER!",
      },
    },
    de: {
      iconPhrases: {
        bone: ["MAMPF!", "KNUSPER!", "LECKER!", "MEINS!"],
        ball: ["FANG!", "HOL!", "ROLL!", "HÜPF!"],
        bowl: ["NÄHM NÄHM!", "MJAM!", "GIB HER!", "SCHLÜRF!"],
        doghouse: ["ZUHAUSE!", "GEMÜTLICH!", "SICHER!", "ZZZ…"],
        "rope-toy": ["ZIEH!", "ZERR!", "GRRR!", "MEINS!"],
        "dog-sleeping": ["Zzz…", "SCHNARCH", "TRÄUM…", "PSCHT…"],
        "dog-skateboard": ["WUSCH!", "VROOM!", "SCHAU!", "OHJE!"],
        paws: ["TAPP TAPP", "TIPP TIPP", "TRAB…", "TRIPP TRAPP"],
      },
      defaultPhrases: ["WUFF!", "WAU!", "WOFF!", "BELL!", "AUUU!"],
      praise: {
        3: "GUTER HUND!",
        7: "WER IST BRAV?",
        15: "BESTER FREUND!",
        30: "HUNDEFLÜSTERER!",
      },
    },
  },
};
