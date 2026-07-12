export const VIEWER_EXPORT_LIMITS = Object.freeze({ maxWidth: 4096, maxHeight: 4096, maxPixels: 16_777_216 });

export function sanitizeViewerFilename(value: string, suffix = "structure-viewer.png") {
  const stem = value.normalize("NFKD").replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^[._-]+|[._-]+$/g, "").slice(0, 80) || "structure";
  return `${stem}-${suffix}`;
}

export function assertViewerExportDimensions(width: number, height: number) {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width <= 0 || height <= 0 || width > VIEWER_EXPORT_LIMITS.maxWidth || height > VIEWER_EXPORT_LIMITS.maxHeight || width * height > VIEWER_EXPORT_LIMITS.maxPixels) {
    throw new Error("VIEWER_EXPORT_SIZE_LIMIT_EXCEEDED");
  }
}

export function downloadLocalBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.rel = "noopener";
  anchor.click();
  queueMicrotask(() => URL.revokeObjectURL(url));
}

export function jsonBlob(payload: unknown) {
  return new Blob([`${JSON.stringify(payload, null, 2)}\n`], { type: "application/json" });
}
