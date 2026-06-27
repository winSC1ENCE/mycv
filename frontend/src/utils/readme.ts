/**
 * README markdown pipeline — separate from the strict `utils/markdown.ts` used
 * for short CV rich-text. README documents are full pages: headings, tables,
 * code blocks and Mermaid diagrams.
 *
 * Mermaid only renders in a browser, and the PDF backend (WeasyPrint) runs no
 * JS — so we render each diagram to SVG here and the same SVG strings power
 * both the live preview and the exported PDF.
 */
import MarkdownIt from "markdown-it";
import DOMPurify from "dompurify";
import type { Mermaid } from "mermaid";

export interface ReadmeContext {
  accessUrl: string;
  expiresAt: string;
  version: string;
  updated: string;
}

const ALLOWED_TAGS = [
  "p",
  "br",
  "hr",
  "strong",
  "em",
  "ul",
  "ol",
  "li",
  "a",
  "code",
  "pre",
  "span",
  "blockquote",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "table",
  "thead",
  "tbody",
  "tr",
  "th",
  "td",
];

const md = new MarkdownIt({ html: false, linkify: true, breaks: true });

// ```mermaid fenced blocks in the source, in document order.
const MERMAID_SOURCE = /```mermaid\s*\n([\s\S]*?)```/g;
// markdown-it renders them as <pre><code class="language-mermaid">…</code></pre>.
const MERMAID_HTML = /<pre><code class="[^"]*language-mermaid[^"]*">[\s\S]*?<\/code><\/pre>/g;

/** Replace the supported `{{token}}` placeholders. Mirrors the PDF backend. */
export function substitutePlaceholders(text: string, ctx: ReadmeContext): string {
  return text
    .replaceAll("{{access_url}}", ctx.accessUrl)
    .replaceAll("{{expires_at}}", ctx.expiresAt)
    .replaceAll("{{version}}", ctx.version)
    .replaceAll("{{updated}}", ctx.updated);
}

/** Extract the source of each ```mermaid block, in order. */
export function extractMermaid(src: string): string[] {
  const blocks: string[] = [];
  for (const match of src.matchAll(MERMAID_SOURCE)) {
    blocks.push(match[1].trim());
  }
  return blocks;
}

let mermaidReady = false;

async function loadMermaid(): Promise<Mermaid> {
  // Dynamic import keeps the (large) mermaid bundle out of the main chunk.
  const mermaid = (await import("mermaid")).default;
  if (!mermaidReady) {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      // htmlLabels would emit <foreignObject>, which WeasyPrint renders poorly.
      htmlLabels: false,
      flowchart: { htmlLabels: false },
    });
    mermaidReady = true;
  }
  return mermaid;
}

/** Render each ```mermaid block to a sanitized SVG string, aligned by index. */
export async function renderMermaidSvgs(src: string): Promise<string[]> {
  const blocks = extractMermaid(src);
  if (blocks.length === 0) return [];
  const mermaid = await loadMermaid();
  const svgs: string[] = [];
  for (let i = 0; i < blocks.length; i++) {
    try {
      const { svg } = await mermaid.render(`rm-diagram-${i}`, blocks[i]);
      svgs.push(DOMPurify.sanitize(svg, { USE_PROFILES: { svg: true, svgFilters: true } }));
    } catch {
      svgs.push('<pre class="mermaid-error">Invalid Mermaid diagram</pre>');
    }
  }
  return svgs;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

/**
 * Build the two badge chips injected at the `{{badges}}` token. The first chip is
 * document-specific (`version` for a README, `reference` for a letter); the second
 * is always the updated date.
 */
export function renderBadges(firstKey: string, firstVal: string, updated: string): string {
  return (
    `<span class="readme-badges">` +
    `<span class="readme-badge">` +
    `<span class="readme-badge__key">${escapeHtml(firstKey)}</span>` +
    `<span class="readme-badge__val">${escapeHtml(firstVal)}</span></span>` +
    `<span class="readme-badge readme-badge--muted">` +
    `<span class="readme-badge__key">updated</span>` +
    `<span class="readme-badge__val">${escapeHtml(updated)}</span></span>` +
    `</span>`
  );
}

/**
 * Render README markdown to sanitized HTML, splicing the pre-rendered Mermaid
 * SVGs back in (in order) and expanding the `{{badges}}` token. Both are injected
 * after sanitizing because they are HTML the markdown renderer would escape; the
 * SVGs are already DOMPurify-sanitized and `badgesHtml` is locally generated.
 */
export function renderReadmeHtml(src: string, svgs: string[], badgesHtml = ""): string {
  const html = DOMPurify.sanitize(md.render(src), {
    ALLOWED_TAGS,
    ALLOWED_ATTR: ["href", "target", "rel", "class"],
  });
  let i = 0;
  const withSvgs = html.replace(MERMAID_HTML, (block) => (i < svgs.length ? svgs[i++] : block));
  return withSvgs.replaceAll("{{badges}}", badgesHtml);
}
