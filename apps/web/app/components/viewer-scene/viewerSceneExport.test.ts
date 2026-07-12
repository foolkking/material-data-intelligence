import { describe, expect, it } from "vitest";

import { assertViewerExportDimensions, jsonBlob, sanitizeViewerFilename } from "./viewerSceneExport";

describe("viewer export security", () => {
  it("sanitizes filenames without retaining paths or markup", () => {
    expect(sanitizeViewerFilename("../../<script> Na Cl")).toBe("script-Na-Cl-structure-viewer.png");
  });

  it("enforces the effective pixel cap", () => {
    expect(() => assertViewerExportDimensions(4096, 4096)).not.toThrow();
    expect(() => assertViewerExportDimensions(4097, 1)).toThrow("VIEWER_EXPORT_SIZE_LIMIT_EXCEEDED");
  });

  it("creates inert JSON blobs", () => {
    const blob = jsonBlob({ label: "<script>" });
    expect(blob.type).toBe("application/json");
    expect(blob.size).toBeGreaterThan(0);
  });
});
