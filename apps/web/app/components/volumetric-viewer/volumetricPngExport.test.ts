import { afterEach, describe, expect, it, vi } from "vitest";

import { createAnnotatedVolumetricPng } from "./volumetricPngExport";

afterEach(() => vi.restoreAllMocks());

describe("volumetric annotated PNG export", () => {
  it("draws a bounded local image and sanitized scientific metadata", async () => {
    const context = { fillStyle: "", font: "", textBaseline: "", imageSmoothingEnabled: true, fillRect: vi.fn(), drawImage: vi.fn(), fillText: vi.fn() };
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(context as unknown as CanvasRenderingContext2D);
    vi.spyOn(HTMLCanvasElement.prototype, "toBlob").mockImplementation((callback) => callback(new Blob(["png"], { type: "image/png" })));
    const source = document.createElement("canvas");
    const result = await createAnnotatedVolumetricPng({ source, outputWidth: 1000, imageHeight: 700, metadataLines: ["field=density\nunit=e/A3", "field_hash=abc"], smoothImage: false });
    expect(result.type).toBe("image/png");
    expect(context.drawImage).toHaveBeenCalledOnce();
    expect(context.fillText).toHaveBeenNthCalledWith(1, "field=density unit=e/A3", 16, 714, 968);
  });

  it("rejects oversized pixels and unbounded metadata before allocation", async () => {
    await expect(createAnnotatedVolumetricPng({ source: document.createElement("canvas"), outputWidth: 4096, imageHeight: 4096, metadataLines: ["x"], smoothImage: true })).rejects.toMatchObject({ code: "VOLUME_VIEWER_BROWSER_CAP_EXCEEDED" });
    await expect(createAnnotatedVolumetricPng({ source: document.createElement("canvas"), outputWidth: 1000, imageHeight: 700, metadataLines: Array(13).fill("x"), smoothImage: true })).rejects.toMatchObject({ code: "VOLUME_VIEWER_BROWSER_CAP_EXCEEDED" });
  });
});
