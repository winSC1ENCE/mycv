import { describe, it, expect, vi, beforeEach } from "vitest";

const useHeadMock = vi.fn();
vi.mock("@unhead/vue", () => ({ useHead: (...args: unknown[]) => useHeadMock(...args) }));

import { usePageMeta } from "@/composables/usePageMeta";

describe("usePageMeta", () => {
  beforeEach(() => {
    useHeadMock.mockClear();
  });

  it("calls useHead with title and description", () => {
    usePageMeta({ title: "My CV", description: "Hello world" });
    expect(useHeadMock).toHaveBeenCalledTimes(1);
    const payload = useHeadMock.mock.calls[0][0];
    expect(payload).toHaveProperty("title");
    expect(payload).toHaveProperty("meta");
  });

  it("includes OG and Twitter meta tags", () => {
    usePageMeta({ title: "T", description: "D" });
    const payload = useHeadMock.mock.calls[0][0];
    const metaNames = (payload.meta as Array<{ property?: string; name?: string }>)
      .map((m) => m.property ?? m.name)
      .filter(Boolean);
    expect(metaNames).toContain("og:title");
    expect(metaNames).toContain("og:description");
    expect(metaNames).toContain("og:image");
    expect(metaNames).toContain("twitter:card");
  });

  it("adds a JSON-LD script tag when jsonLd is provided", () => {
    usePageMeta({
      title: "T",
      description: "D",
      jsonLd: () => ({ "@type": "Person", name: "X" }),
    });
    const payload = useHeadMock.mock.calls[0][0];
    expect(payload.script).toHaveLength(1);
    expect(payload.script[0].type).toBe("application/ld+json");
  });

  it("accepts function sources for reactive values", () => {
    usePageMeta({ title: () => "Lazy Title", description: () => "Lazy Desc" });
    expect(useHeadMock).toHaveBeenCalled();
  });
});
