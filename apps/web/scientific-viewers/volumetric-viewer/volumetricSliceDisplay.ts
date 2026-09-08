import { volumePalette } from "./volumetricVolumeModel";
import type { VolumeTransferFunction, VolumetricSlice } from "./volumetricViewerTypes";

export function sliceRgba(slice: VolumetricSlice, transferFunction: VolumeTransferFunction): Uint8Array {
  const output = new Uint8Array(slice.values.length * 4);
  const span = transferFunction.windowHigh - transferFunction.windowLow;
  slice.values.forEach((value, index) => {
    const normalized = Math.min(1, Math.max(0, (value - transferFunction.windowLow) / span));
    const color = volumePalette(normalized, transferFunction.paletteId);
    output[index * 4] = Math.round(color[0] * 255);
    output[index * 4 + 1] = Math.round(color[1] * 255);
    output[index * 4 + 2] = Math.round(color[2] * 255);
    output[index * 4 + 3] = 255;
  });
  return output;
}
