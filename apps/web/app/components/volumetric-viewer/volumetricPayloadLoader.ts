import { gunzipSync } from "fflate";

import { getPlannerArtifactContent } from "../../lib/planner-api";
import type {
  DecodedVolumetricField,
  ValidatedVolumetricField,
  ValidatedVolumetricPayload,
  VolumetricArtifact,
} from "./volumetricViewerTypes";
import { VOLUMETRIC_BROWSER_CAPS, VolumetricViewerError } from "./volumetricViewerTypes";

export type VolumetricByteLoader = (
  artifact: VolumetricArtifact,
  options: Readonly<{ signal?: AbortSignal; maximumBytes: number }>,
) => Promise<ArrayBuffer>;

export const defaultVolumetricByteLoader: VolumetricByteLoader = async (artifact, options) => {
  const jobId = artifact.jobId;
  const artifactId = artifact.id ?? artifact.artifactId;
  if (!jobId || !artifactId) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_LOAD_FAILED", "Artifact identity is unavailable.");
  return getPlannerArtifactContent(jobId, artifactId, options);
};

export async function loadVolumetricJsonArtifact(
  artifact: VolumetricArtifact | undefined,
  options: Readonly<{ signal?: AbortSignal; loader?: VolumetricByteLoader; maximumBytes?: number }> = {},
): Promise<unknown> {
  if (!artifact) throw new VolumetricViewerError("VOLUME_VIEWER_ARTIFACTS_MISSING", "Required volumetric metadata is missing.");
  const attached = artifact.content ?? artifact.payload ?? artifact.metadata?.preview;
  const retrievable = Boolean(artifact.jobId && (artifact.id ?? artifact.artifactId));
  if (!retrievable && attached !== undefined) return parseAttachedJson(attached);
  const maximumBytes = Math.min(options.maximumBytes ?? 4_194_304, 4_194_304);
  const bytes = await (options.loader ?? defaultVolumetricByteLoader)(artifact, { signal: options.signal, maximumBytes });
  await verifyArtifactHash(artifact, bytes);
  try {
    return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
  } catch {
    throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Volumetric metadata is not valid UTF-8 JSON.");
  }
}

export async function loadDecodedVolumetricField(args: Readonly<{
  field: ValidatedVolumetricField;
  payload: ValidatedVolumetricPayload;
  artifacts: readonly VolumetricArtifact[];
  signal?: AbortSignal;
  loader?: VolumetricByteLoader;
}>): Promise<DecodedVolumetricField> {
  const { field, payload, artifacts, signal } = args;
  if (payload.uncompressedBytes > VOLUMETRIC_BROWSER_CAPS.maximumPayloadBytes) {
    throw new VolumetricViewerError("VOLUME_VIEWER_BROWSER_CAP_EXCEEDED", "Field payload exceeds the browser byte budget.");
  }
  const started = now();
  let decompressionMs = 0;
  let hashValidationMs = 0;
  let buffer: ArrayBuffer;
  if (payload.encoding === "inline_json") {
    buffer = encodeInline(payload);
  } else if (payload.encoding === "chunked_binary") {
    buffer = new ArrayBuffer(payload.uncompressedBytes);
    const target = new Uint8Array(buffer);
    let offset = 0;
    for (const chunk of payload.chunks) {
      assertNotAborted(signal);
      const artifact = requiredArtifact(artifacts, chunk.artifactName);
      const stored = await readStored(artifact, chunk.compressedBytes, signal, args.loader);
      const hashStarted = now();
      await assertSha256(stored, chunk.storageSha256, "VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH");
      hashValidationMs += elapsed(hashStarted);
      const decompressionStarted = now();
      const logical = chunk.encoding === "gzip_binary" ? decompressGzip(stored, chunk.uncompressedBytes) : stored;
      decompressionMs += elapsed(decompressionStarted);
      const logicalHashStarted = now();
      await assertSha256(logical, chunk.logicalSha256, "VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH");
      hashValidationMs += elapsed(logicalHashStarted);
      if (offset + logical.byteLength > target.byteLength) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Chunk bytes exceed the logical payload.");
      target.set(new Uint8Array(logical), offset);
      offset += logical.byteLength;
    }
    if (offset !== target.byteLength) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Chunk bytes do not fill the logical payload.");
  } else {
    const artifact = requiredArtifact(artifacts, String(payload.artifactName));
    const stored = await readStored(artifact, payload.compressedBytes, signal, args.loader);
    const storageHashStarted = now();
    await assertSha256(stored, payload.storageSha256, "VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH");
    hashValidationMs += elapsed(storageHashStarted);
    const decompressionStarted = now();
    buffer = payload.encoding === "gzip_binary" ? decompressGzip(stored, payload.uncompressedBytes) : stored;
    decompressionMs += elapsed(decompressionStarted);
  }
  assertNotAborted(signal);
  if (buffer.byteLength !== payload.uncompressedBytes) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Decoded field byte length does not match metadata.");
  const logicalHashStarted = now();
  await assertSha256(buffer, payload.logicalSha256, "VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH");
  hashValidationMs += elapsed(logicalHashStarted);
  assertFiniteValues(buffer, payload.dtype, payload.valueCount);
  return Object.freeze({
    field,
    payload,
    buffer,
    byteLength: buffer.byteLength,
    fetchMs: round(elapsed(started) - decompressionMs - hashValidationMs),
    decompressionMs: round(decompressionMs),
    hashValidationMs: round(hashValidationMs),
  });
}

export async function sha256Hex(value: ArrayBuffer): Promise<string> {
  if (!globalThis.crypto?.subtle) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH", "SHA-256 is unavailable in this browser.");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", value);
  return [...new Uint8Array(digest)].map((item) => item.toString(16).padStart(2, "0")).join("");
}

function parseAttachedJson(value: unknown): unknown {
  if (typeof value !== "string") return value;
  if (new TextEncoder().encode(value).byteLength > 4_194_304) throw new VolumetricViewerError("VOLUME_VIEWER_BROWSER_CAP_EXCEEDED", "Volumetric metadata exceeds the browser cap.");
  try { return JSON.parse(value); } catch { throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Volumetric metadata is not valid JSON."); }
}

function encodeInline(payload: ValidatedVolumetricPayload): ArrayBuffer {
  if (!payload.inlineValues || payload.inlineValues.length !== payload.valueCount) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Inline field values are incomplete.");
  const buffer = new ArrayBuffer(payload.uncompressedBytes);
  const view = new DataView(buffer);
  const stride = payload.dtype === "float32" ? 4 : 8;
  payload.inlineValues.forEach((value, index) => {
    if (!Number.isFinite(value)) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Field values must be finite.");
    if (payload.dtype === "float32") view.setFloat32(index * stride, Object.is(value, -0) ? 0 : value, true);
    else view.setFloat64(index * stride, Object.is(value, -0) ? 0 : value, true);
  });
  return buffer;
}

function decompressGzip(stored: ArrayBuffer, expectedBytes: number): ArrayBuffer {
  if (stored.byteLength <= 0 || expectedBytes > VOLUMETRIC_BROWSER_CAPS.maximumPayloadBytes || expectedBytes > stored.byteLength * 128) throw new VolumetricViewerError("VOLUME_VIEWER_DECOMPRESSION_FAILED", "Gzip payload exceeds decompression limits.");
  const bytes = new Uint8Array(stored);
  if (bytes[0] !== 0x1f || bytes[1] !== 0x8b || bytes[2] !== 8) throw new VolumetricViewerError("VOLUME_VIEWER_DECOMPRESSION_FAILED", "Gzip header is invalid.");
  try {
    const output = gunzipSync(bytes);
    if (output.byteLength !== expectedBytes) throw new Error("length");
    return output.buffer.slice(output.byteOffset, output.byteOffset + output.byteLength) as ArrayBuffer;
  } catch {
    throw new VolumetricViewerError("VOLUME_VIEWER_DECOMPRESSION_FAILED", "Gzip payload could not be decoded safely.");
  }
}

async function readStored(artifact: VolumetricArtifact, expectedBytes: number, signal: AbortSignal | undefined, loader: VolumetricByteLoader | undefined): Promise<ArrayBuffer> {
  assertNotAborted(signal);
  const declared = artifact.sizeBytes;
  if (declared !== undefined && declared !== expectedBytes) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Artifact size does not match payload metadata.");
  const attached = artifact.content;
  let buffer: ArrayBuffer;
  if (attached instanceof ArrayBuffer) buffer = attached.slice(0);
  else if (ArrayBuffer.isView(attached)) buffer = attached.buffer.slice(attached.byteOffset, attached.byteOffset + attached.byteLength) as ArrayBuffer;
  else buffer = await (loader ?? defaultVolumetricByteLoader)(artifact, { signal, maximumBytes: Math.min(expectedBytes, VOLUMETRIC_BROWSER_CAPS.maximumPayloadBytes) });
  if (buffer.byteLength !== expectedBytes) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Artifact bytes do not match payload metadata.");
  await verifyArtifactHash(artifact, buffer);
  return buffer;
}

async function verifyArtifactHash(artifact: VolumetricArtifact, bytes: ArrayBuffer): Promise<void> {
  const expected = artifact.sha256 ?? artifact.contentHash;
  if (expected && !/^[0-9a-f]{64}$/.test(expected)) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH", "Artifact hash metadata is invalid.");
  if (expected) await assertSha256(bytes, expected, "VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH");
}

async function assertSha256(bytes: ArrayBuffer, expected: string, code: "VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH"): Promise<void> {
  if (await sha256Hex(bytes) !== expected) throw new VolumetricViewerError(code, "Artifact content hash does not match validated metadata.");
}

function assertFiniteValues(buffer: ArrayBuffer, dtype: "float32" | "float64", expectedCount: number): void {
  const stride = dtype === "float32" ? 4 : 8;
  if (buffer.byteLength !== expectedCount * stride) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Field value count does not match payload metadata.");
  const view = new DataView(buffer);
  for (let offset = 0; offset < buffer.byteLength; offset += stride) {
    const value = dtype === "float32" ? view.getFloat32(offset, true) : view.getFloat64(offset, true);
    if (!Number.isFinite(value)) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Decoded field contains a non-finite value.");
  }
}

function requiredArtifact(artifacts: readonly VolumetricArtifact[], name: string): VolumetricArtifact {
  const matches = artifacts.filter((artifact) => artifact.name === name);
  if (matches.length !== 1) throw new VolumetricViewerError("VOLUME_VIEWER_ARTIFACTS_MISSING", `Required numeric payload ${name} is unavailable.`);
  return matches[0];
}

function assertNotAborted(signal?: AbortSignal): void {
  if (signal?.aborted) throw new VolumetricViewerError("VOLUME_VIEWER_EXTRACTION_CANCELLED", "Volumetric loading was cancelled.");
}
function now(){return typeof performance==="undefined"?Date.now():performance.now();}
function elapsed(start:number){return Math.max(0,now()-start);}
function round(value:number){return Math.round(Math.max(0,value)*1000)/1000;}
