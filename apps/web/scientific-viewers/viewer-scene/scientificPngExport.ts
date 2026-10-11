export function captureScientificCanvas(source: HTMLCanvasElement): HTMLCanvasElement {
  if (source.width < 1 || source.height < 1 || source.width * source.height > 16_777_216) throw new Error("VIEWER_EXPORT_PIXEL_LIMIT");
  const snapshot = document.createElement("canvas");
  snapshot.width = source.width;
  snapshot.height = source.height;
  try {
    const context = snapshot.getContext("2d");
    if (!context) throw new Error("VIEWER_EXPORT_CANVAS_UNAVAILABLE");
    context.drawImage(source, 0, 0);
    return snapshot;
  } catch (error) {
    snapshot.width = 0; snapshot.height = 0;
    throw error;
  }
}

export async function encodeScientificPng(canvas: HTMLCanvasElement, prefix = "VIEWER_EXPORT"): Promise<Blob> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await new Promise<Blob>((resolve, reject) => {
      timer = setTimeout(() => reject(new Error(`${prefix}_TIMEOUT`)), 15_000);
      canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error(`${prefix}_FAILED`)), "image/png");
    });
  } finally {
    if (timer) clearTimeout(timer);
    canvas.width = 0; canvas.height = 0;
  }
}

export function createScientificPngExporter<T = void>(capture: (request: T) => HTMLCanvasElement) {
  let busy = false;
  return async (request: T): Promise<Blob> => {
    if (busy) throw new Error("VIEWER_EXPORT_IN_PROGRESS");
    busy = true;
    try { return await encodeScientificPng(capture(request)); }
    finally { busy = false; }
  };
}

export async function decodeScientificImage(blob: Blob): Promise<ImageBitmap> {
  let expired = false;
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await new Promise<ImageBitmap>((resolve, reject) => {
      timer = setTimeout(() => { expired = true; reject(new Error("VIEWER_EXPORT_DECODE_TIMEOUT")); }, 15_000);
      createImageBitmap(blob).then(bitmap => { if (expired) bitmap.close(); else resolve(bitmap); }, reject);
    });
  } finally { if (timer) clearTimeout(timer); }
}
