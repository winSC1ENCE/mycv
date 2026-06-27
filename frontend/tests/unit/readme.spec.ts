import { describe, expect, it, vi } from "vitest";
import {
  extractMermaid,
  renderBadges,
  renderMermaidSvgs,
  renderReadmeHtml,
  substitutePlaceholders,
  type ReadmeContext,
} from "@/utils/readme";

// jsdom can't run mermaid's real renderer — mock it to a deterministic SVG.
vi.mock("mermaid", () => ({
  default: {
    initialize: vi.fn(),
    render: vi.fn(async (_id: string, src: string) => {
      if (src.includes("BAD")) throw new Error("parse error");
      return { svg: `<svg data-src="${src.replace(/\s+/g, "_")}">ok</svg>` };
    }),
  },
}));

const CTX: ReadmeContext = {
  accessUrl: "https://cv.test/?key=abc",
  expiresAt: "30.06.2026 23:59",
  version: "v1.0.0",
  updated: "26.06.2026",
};

describe("substitutePlaceholders", () => {
  it("replaces every supported token", () => {
    const out = substitutePlaceholders(
      "open {{access_url}} until {{expires_at}} {{version}} {{updated}}",
      CTX,
    );
    expect(out).toBe("open https://cv.test/?key=abc until 30.06.2026 23:59 v1.0.0 26.06.2026");
  });

  it("replaces repeated tokens", () => {
    expect(substitutePlaceholders("{{version}} {{version}}", CTX)).toBe("v1.0.0 v1.0.0");
  });
});

describe("extractMermaid", () => {
  it("returns blocks in document order", () => {
    const src = "```mermaid\nflowchart TD\nA-->B\n```\n\ntext\n\n```mermaid\ngraph LR\nC-->D\n```";
    expect(extractMermaid(src)).toEqual(["flowchart TD\nA-->B", "graph LR\nC-->D"]);
  });

  it("returns empty array when no diagrams", () => {
    expect(extractMermaid("# just text")).toEqual([]);
  });
});

describe("renderMermaidSvgs", () => {
  it("renders each block to a sanitized svg", async () => {
    const svgs = await renderMermaidSvgs("```mermaid\nflowchart TD\nA-->B\n```");
    expect(svgs).toHaveLength(1);
    expect(svgs[0]).toContain("<svg");
  });

  it("returns an error placeholder when a diagram fails", async () => {
    const svgs = await renderMermaidSvgs("```mermaid\nBAD\n```");
    expect(svgs[0]).toContain("mermaid-error");
  });

  it("returns empty array without diagrams", async () => {
    expect(await renderMermaidSvgs("plain")).toEqual([]);
  });
});

describe("renderReadmeHtml", () => {
  it("renders headings and tables", () => {
    const html = renderReadmeHtml("# Title\n\n| a | b |\n|---|---|\n| 1 | 2 |", []);
    expect(html).toContain("<h1>Title</h1>");
    expect(html).toContain("<table>");
    expect(html).toContain("<td>1</td>");
  });

  it("splices svgs into mermaid blocks in order", () => {
    const src = "```mermaid\nflowchart TD\nA-->B\n```\n\n```mermaid\ngraph LR\nC-->D\n```";
    const html = renderReadmeHtml(src, ["<svg>ONE</svg>", "<svg>TWO</svg>"]);
    expect(html).toContain("<svg>ONE</svg>");
    expect(html).toContain("<svg>TWO</svg>");
    expect(html).not.toContain("language-mermaid");
    expect(html.indexOf("ONE")).toBeLessThan(html.indexOf("TWO"));
  });

  it("leaves the code block when no svg is supplied", () => {
    const html = renderReadmeHtml("```mermaid\nflowchart TD\nA-->B\n```", []);
    expect(html).toContain("language-mermaid");
  });

  it("expands the {{badges}} token with the supplied badge markup", () => {
    const badges = renderBadges("v1.2.3", "26.06.2026");
    const html = renderReadmeHtml("# Title\n\n{{badges}}\n\nbody", [], badges);
    expect(html).toContain("<h1>Title</h1>");
    expect(html).toContain("readme-badges");
    expect(html).toContain("v1.2.3");
    expect(html).not.toContain("{{badges}}");
  });
});

describe("renderBadges", () => {
  it("outputs version and updated chips", () => {
    const html = renderBadges("v2.0.0", "01.01.2026");
    expect(html).toContain("readme-badge");
    expect(html).toContain("v2.0.0");
    expect(html).toContain("01.01.2026");
  });

  it("escapes HTML in the values", () => {
    expect(renderBadges("<script>", "x")).not.toContain("<script>");
    expect(renderBadges("<script>", "x")).toContain("&lt;script&gt;");
  });
});
