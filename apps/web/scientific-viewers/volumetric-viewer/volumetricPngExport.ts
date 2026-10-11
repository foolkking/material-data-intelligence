import { VOLUMETRIC_BROWSER_CAPS, VolumetricViewerError } from "./volumetricViewerTypes";
import { decodeScientificImage, encodeScientificPng } from "../viewer-scene/scientificPngExport";

export async function createAnnotatedVolumetricPng(args: Readonly<{
  source: HTMLCanvasElement | Blob;
  outputWidth: number;
  imageHeight: number;
  metadataLines: readonly string[];
  smoothImage: boolean;
}>): Promise<Blob> {
  if (!Number.isSafeInteger(args.outputWidth) || !Number.isSafeInteger(args.imageHeight)
    || args.outputWidth < 256 || args.imageHeight < 256
    || args.outputWidth > VOLUMETRIC_BROWSER_CAPS.maximumExportDimension
    || args.imageHeight > VOLUMETRIC_BROWSER_CAPS.maximumExportDimension
    || args.metadataLines.length < 1 || args.metadataLines.length > 12) {
    throw new VolumetricViewerError("VOLUME_VIEWER_BROWSER_CAP_EXCEEDED", "PNG annotation request exceeds the bounded export policy.");
  }
  const lines = args.metadataLines.map(sanitizeLine);
  const captionHeight = 30 + lines.length * 22;
  const totalHeight = args.imageHeight + captionHeight;
  if (args.outputWidth * totalHeight > VOLUMETRIC_BROWSER_CAPS.maximumExportPixels) {
    throw new VolumetricViewerError("VOLUME_VIEWER_BROWSER_CAP_EXCEEDED", "Annotated PNG exceeds the bounded pixel budget.");
  }
  const canvas = document.createElement("canvas");
  canvas.width = args.outputWidth;
  canvas.height = totalHeight;
  const context = canvas.getContext("2d");
  if (!context) throw new VolumetricViewerError("VOLUME_VIEWER_RENDERER_FAILED", "Local PNG annotation canvas is unavailable.");
  context.fillStyle = "#f7f9fb";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.imageSmoothingEnabled = args.smoothImage;
  let bitmap: ImageBitmap | null = null;
  try {
    const source: CanvasImageSource = args.source instanceof Blob
      ? (bitmap = await decodeScientificImage(args.source))
      : args.source;
    const scale = Math.min(args.outputWidth / source.width, args.imageHeight / source.height);
    if (!Number.isFinite(scale) || scale <= 0) throw new Error("VIEWER_EXPORT_EMPTY_IMAGE");
    const width = source.width * scale, height = source.height * scale;
    context.drawImage(source, (args.outputWidth - width) / 2, (args.imageHeight - height) / 2, width, height);
    context.fillStyle = "#17232b";
    context.fillRect(0, args.imageHeight, args.outputWidth, captionHeight);
    context.fillStyle = "#f7f9fb";
    context.font = "14px system-ui, sans-serif";
    context.textBaseline = "top";
    lines.forEach((line, index) => context.fillText(line, 16, args.imageHeight + 14 + index * 22, args.outputWidth - 32));
    return await encodeScientificPng(canvas);
  } finally {
    bitmap?.close();
    canvas.width = 1;
    canvas.height = 1;
  }
}

function sanitizeLine(value: string): string {
  return value.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, 180);
}
