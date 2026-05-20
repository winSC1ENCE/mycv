/**
 * Phrase pools for the Dog Mode "pet the icon" game.
 *
 * Each icon bucket maps to 3–5 onomatopoeic phrases. URL → bucket is by
 * substring match (the dog icons live at `/icons/dog/<name>.png`).
 */

const PHRASES: Record<string, string[]> = {
  bone: ["YUM!", "CRUNCH!", "TASTY!", "MINE!"],
  ball: ["FETCH!", "CATCH!", "ROLL!", "BOUNCE!"],
  bowl: ["NOM NOM!", "YUMMY!", "GIMME!", "SLURP!"],
  doghouse: ["HOME!", "COZY!", "SAFE!", "ZZZ…"],
  "rope-toy": ["TUG!", "PULL!", "GRRR!", "MINE!"],
  "dog-sleeping": ["Zzz…", "SNORE", "DREAM…", "SHHH…"],
  "dog-skateboard": ["WHEE!", "VROOM!", "LOOK!", "YIKES!"],
  paws: ["TAP TAP", "PAT PAT", "TROT…", "STEP STEP"],
};

const DEFAULT_PHRASES = ["WUFF!", "BARK!", "WOOF!", "BORK!", "AWOOO!"];

const PRAISE: Record<number, string> = {
  3: "GOOD DOG!",
  7: "WHO'S A GOOD BOY?",
  15: "BEST FRIEND!",
  30: "DOG WHISPERER!",
};

export function phrasesForIcon(url: string): string[] {
  for (const key of Object.keys(PHRASES)) {
    if (url.includes(key)) return PHRASES[key];
  }
  return DEFAULT_PHRASES;
}

export function randomPhrase(url: string): string {
  const pool = phrasesForIcon(url);
  return pool[Math.floor(Math.random() * pool.length)];
}

export function praiseFor(count: number): string | null {
  return PRAISE[count] ?? null;
}
