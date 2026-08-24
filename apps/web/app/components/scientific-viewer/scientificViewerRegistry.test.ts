import { describe, expect, it } from "vitest";

import { listScientificViewerCapabilities, resolveScientificViewer } from "./scientificViewerRegistry";

describe("Agent2 Phase 9 ScientificViewerRegistry", () => {
  it("resolves canonical and legacy scientific types deterministically without an LLM", () => {
    expect(resolveScientificViewer({ objectType: "structure.crystal" }).rendererKey).toBe("structure-3d");
    expect(resolveScientificViewer({ objectType: "Structure" }).scientificType).toBe("structure.crystal");
    expect(resolveScientificViewer({ objectType: "DataFrame", semanticRole: "experimental_xrd" }).rendererKey).toBe("xrd");
    expect(resolveScientificViewer({ objectType: "DataFrame", schemaVersion: "trajectory.rdf.v1" }).rendererKey).toBe("rdf");
  });

  it("classifies every canonical high-value viewer and returns an explicit safe fallback", () => {
    const keys = new Set(listScientificViewerCapabilities().map((item) => item.rendererKey));
    for (const key of ["scientific-table", "structure-3d", "trajectory", "xrd", "rdf", "band-structure", "density-of-states", "phonon-band", "phonon-dos", "brillouin-zone", "volumetric"]) {
      expect(keys.has(key)).toBe(true);
    }
    expect(resolveScientificViewer({ objectType: "archive.generic" })).toMatchObject({ support: "FALLBACK", rendererKey: "generic-safe-fallback" });
  });
});
