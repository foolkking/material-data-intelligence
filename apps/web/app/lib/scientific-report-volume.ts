import { deflate } from "node:zlib";
import type { ReportViewerArtifact } from "./scientific-report-api";
import { escapeReportHtml as html } from "./scientific-report-figure";
import { validateVolumetricArtifacts } from "../../scientific-viewers/volumetric-viewer/volumetricValidation";
import { loadDecodedVolumetricField } from "../../scientific-viewers/volumetric-viewer/volumetricPayloadLoader";
import { gridIndexToFractional, sampleVolumetricSlice } from "../../scientific-viewers/volumetric-viewer/volumetricSliceModel";
import { volumePalette } from "../../scientific-viewers/volumetric-viewer/volumetricVolumeModel";
import type { VolumetricSlice } from "../../scientific-viewers/volumetric-viewer/volumetricViewerTypes";
import { densityFieldName, densityUnit } from "../../scientific-viewers/volumetric-viewer/density-display";

export type SavedVolumeView = { svg: string; compactSvg: string; sampleCount: number; data: string };

/** Render exact saved grid planes, with no interpolation, unit conversion or new analysis. */
export async function renderReportVolume(
  artifacts: ReportViewerArtifact[], read: (artifact: ReportViewerArtifact) => Promise<Uint8Array>, signal: AbortSignal,
): Promise<{ views: SavedVolumeView[]; unsupportedFields: string[] }> {
  if (!artifacts.length || new Set(artifacts.map(a => a.name)).size !== artifacts.length
    || artifacts.some(a => a.jobId !== artifacts[0].jobId || a.toolCallId !== artifacts[0].toolCallId)) throw new Error("Ambiguous volumetric source");
  const one = (type: string) => {
    const matches = artifacts.filter(a => a.type === type);
    if (matches.length !== 1) throw new Error("Missing or ambiguous volumetric metadata");
    return matches[0];
  };
  const datasetArtifact = one("volumetric_dataset_json"), manifestArtifact = one("volumetric_manifest_json");
  const dataset = JSON.parse(new TextDecoder().decode(await read(datasetArtifact)));
  const manifest = JSON.parse(new TextDecoder().decode(await read(manifestArtifact)));
  const validation = validateVolumetricArtifacts(dataset, manifest);
  if (!validation.ok) throw new Error(`Invalid volumetric source: ${validation.code}`);
  // Manifest names resolve only inside this exact producer's descriptor list.
  for (const entry of manifest.artifacts) {
    const matches = artifacts.filter(a => a.name === entry.name);
    if (matches.length !== 1 || matches[0].sha256 !== entry.sha256 || matches[0].sizeBytes !== entry.bytes) throw new Error("Volumetric manifest dependency mismatch");
  }
  const { bundle } = validation;
  const views: SavedVolumeView[] = [], unsupportedFields: string[] = [];
  for (const item of bundle.fields) {
    signal.throwIfAborted();
    if (!item.supported) { unsupportedFields.push(item.field.fieldName); continue; }
    const decoded = await loadDecodedVolumetricField({ ...item, artifacts, signal, loader: async artifact => {
      const matches = artifacts.filter(a => a.id === artifact.id && a.jobId === artifact.jobId);
      if (matches.length !== 1) throw new Error("Unbound volumetric dependency");
      const bytes = await read(matches[0]);
      return bytes.slice().buffer as ArrayBuffer;
    } });
    for (const axis of [0, 1, 2] as const) {
      signal.throwIfAborted();
      const index = Math.floor(bundle.grid.shape[axis] / 2);
      const fractionalPosition = gridIndexToFractional(bundle.grid, axis, index);
      const slice = await sampleVolumetricSlice({ datasetHash: bundle.datasetContentHash, fieldHash: item.field.contentHash,
        unit: item.field.unit, grid: bundle.grid, dtype: item.payload.dtype, fieldBuffer: decoded.buffer,
        axis, fractionalPosition, maximumOutputValues: 512 * 512 });
      if (slice.samplingMode !== "exact_grid_plane") throw new Error("Report plane must use exact saved nodes");
      const png = await slicePng(slice);
      signal.throwIfAborted();
      const data = JSON.stringify({
        schema_version: "mdi.report-volumetric-plane/1.0", dataset_artifact_id: datasetArtifact.id,
        dataset_hash: bundle.datasetContentHash, field_id: item.field.fieldId, field_hash: item.field.contentHash,
        field_name: item.field.fieldName, unit: item.field.unit, axis, grid_index: index,
        fractional_position: slice.fractionalPosition, sampling: slice.samplingMode,
        horizontal_axis: slice.plane.horizontalAxis, vertical_axis: slice.plane.verticalAxis,
        shape: slice.outputShape, values: Array.from(slice.values),
      }, null, 2) + "\n";
      views.push({ svg: planeSvg(slice, densityFieldName(item.field), png, 640), compactSvg: planeSvg(slice, densityFieldName(item.field), png, 360),
        sampleCount: slice.values.length, data });
    }
  }
  return { views, unsupportedFields };
}

async function slicePng(slice: VolumetricSlice): Promise<Uint8Array> {
  const [height, width] = slice.outputShape;
  const { minimum: low, maximum: high } = slice.statistics;
  const raw = new Uint8Array(height * (width * 3 + 1));
  for (let row = 0; row < height; row++) {
    for (let column = 0; column < width; column++) {
      const value = slice.values[(height - row - 1) * width + column];
      const color = volumePalette(high === low ? 0.5 : (value - low) / (high - low), "viridis");
      const offset = row * (width * 3 + 1) + 1 + column * 3;
      for (let channel = 0; channel < 3; channel++) raw[offset + channel] = Math.round(color[channel] * 255);
    }
  }
  const compressed = await new Promise<Buffer>((resolve, reject) => deflate(raw, (error, bytes) => error ? reject(error) : resolve(bytes)));
  const header = Buffer.alloc(13); header.writeUInt32BE(width); header.writeUInt32BE(height, 4); header[8] = 8; header[9] = 2;
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]), pngChunk("IHDR", header), pngChunk("IDAT", compressed), pngChunk("IEND", Buffer.alloc(0))]);
}

function pngChunk(type: string, bytes: Uint8Array): Buffer {
  const output = Buffer.alloc(bytes.length + 12);
  output.writeUInt32BE(bytes.length); output.write(type, 4); output.set(bytes, 8);
  let crc = 0xffffffff;
  for (const byte of output.subarray(4, output.length - 4)) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  output.writeUInt32BE((crc ^ 0xffffffff) >>> 0, output.length - 4);
  return output;
}

function planeSvg(slice: VolumetricSlice, field: string, png: Uint8Array, width: number): string {
  const compact = width === 360;
  const size = compact ? 232 : 480, left = (width - size) / 2 + 8;
  const [rows, columns] = slice.outputShape;
  const imageWidth = size * Math.min(1, columns / rows);
  const imageHeight = size * Math.min(1, rows / columns);
  const imageLeft = left + (size - imageWidth) / 2;
  const plotHeight = Math.max(192, imageHeight);
  // Units remain complete, including long compound units on narrow exports.
  const lines = (text: string, capacity: number) => {
    const result: string[] = []; let line = "", used = 0;
    for (const character of text) {
      const weight = character.charCodeAt(0) > 255 ? 2 : 1;
      if (used + weight > capacity) { result.push(line); line = ""; used = 0; }
      line += character; used += weight;
    }
    if (line) result.push(line);
    return result;
  };
  const unitLines = lines(densityUnit(slice.unit), compact ? 30 : 60);
  const top = 112 + Math.max(0, unitLines.length - 1) * 18, height = top + plotHeight + 128;
  const imageTop = top + (plotHeight - imageHeight) / 2;
  const { minimum: low, maximum: high } = slice.statistics;
  const title = `${field} · 晶格轴 ${slice.axis} = ${slice.fractionalPosition}`;
  const number = (value: number) => Number(value.toPrecision(8)).toString();
  const fieldLines = lines(field, compact ? 26 : 50);
  const fieldLabel = (fieldLines[0] || "") + (fieldLines.length > 1 ? "…" : "");
  const stops = [0, 0.25, 0.5, 0.75, 1].map(value => {
    const color = volumePalette(value, "viridis").map(channel => Math.round(channel * 255));
    return `<stop offset="${value * 100}%" stop-color="rgb(${color.join(",")})"/>`;
  }).join("");
  const scale = low === high ? `<text x="${left}" y="${top + plotHeight + 62}" font-size="14">全部样本值：${number(low)}</text>`
    : `<defs><linearGradient id="scale">${stops}</linearGradient></defs><rect x="${left}" y="${top + plotHeight + 40}" width="${size}" height="10" fill="url(#scale)"/>
<text x="${left}" y="${top + plotHeight + 72}" font-size="14">最小：${number(low)}</text><text x="${left}" y="${top + plotHeight + 94}" font-size="14">最大：${number(high)}</text>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${html(title)}">
<title>${html(title)} · ${html(densityUnit(slice.unit))}</title><rect width="100%" height="100%" fill="#fff"/><g font-family="sans-serif" fill="#243833">
<text x="${left}" y="26" font-size="18">${html(fieldLabel)}</text><text x="${left}" y="49" font-size="14">晶格轴 ${slice.axis} = ${number(slice.fractionalPosition)}</text>
<text x="${left}" y="71" font-size="14">精确网格平面 · ${slice.outputShape.join(" × ")}</text><text font-size="14">${unitLines.map((line, index) => `<tspan x="${left}" y="${94 + index * 18}">${html(line)}</tspan>`).join("")}</text>
<image x="${imageLeft}" y="${imageTop}" width="${imageWidth}" height="${imageHeight}" preserveAspectRatio="xMidYMid meet" style="image-rendering:pixelated" href="data:image/png;base64,${Buffer.from(png).toString("base64")}"/>
<text x="${left + size / 2}" y="${top + plotHeight + 26}" text-anchor="middle" font-size="14">晶格轴 ${slice.plane.horizontalAxis} · 网格索引 0–${slice.outputShape[1] - 1}</text>
<text transform="translate(${imageLeft - 44} ${top + plotHeight / 2}) rotate(-90)" text-anchor="middle" font-size="14">晶格轴 ${slice.plane.verticalAxis} · 网格索引 0–${slice.outputShape[0] - 1}</text>
${scale}
</g></svg>`;
}
