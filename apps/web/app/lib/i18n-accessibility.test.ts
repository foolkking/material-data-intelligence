import { describe, expect, it } from "vitest";

import { dictionaries } from "./i18n";

const canonicalTermKeys = [
  "termDataset",
  "termProfile",
  "termAnalysis",
  "termPlan",
  "termResult",
  "termArtifact",
  "termFinding",
  "termEvidence",
  "termProvenance",
  "termWorkspace",
  "termReport",
  "termRecipe",
  "termSelection",
  "termLimitation",
  "termWarning",
  "termUnavailable",
  "termUnsupported",
  "termPartial",
] as const;

describe("Phase 12-6 terminology and accessibility foundation", () => {
  it("keeps canonical scientific UI terms complete in both supported catalogs", () => {
    for (const key of canonicalTermKeys) {
      expect(dictionaries["en-US"][key].trim()).not.toBe("");
      expect(dictionaries["zh-CN"][key].trim()).not.toBe("");
    }
  });

  it("provides localized skip-navigation labels", () => {
    expect(dictionaries["en-US"].skipToAnalysis).toBe("Skip to analysis workspace");
    expect(dictionaries["zh-CN"].skipToAnalysis).not.toBe(dictionaries["en-US"].skipToAnalysis);
  });
});
