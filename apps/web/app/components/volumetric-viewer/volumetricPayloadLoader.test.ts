import { createHash } from "node:crypto";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { loadDecodedVolumetricField, sha256Hex } from "./volumetricPayloadLoader";
import type { ValidatedVolumetricField, ValidatedVolumetricPayload } from "./volumetricViewerTypes";

const field = { fieldId: "field:test", fieldName: "density", contentHash: "a".repeat(64) } as ValidatedVolumetricField;
const payloadBase = { schemaVersion: "phase10j.volumetric_payload.v1", payloadId: "payload:test", gridShape: [1, 1, 2], compressedBytes: 8, storageSha256: "0".repeat(64), artifactName: null, chunks: [] } as unknown as ValidatedVolumetricPayload;

beforeEach(() => vi.stubGlobal("crypto", { subtle: { digest: async (_algorithm: string, value: BufferSource) => {
  const bytes = new Uint8Array(value instanceof ArrayBuffer ? value : value.buffer, value instanceof ArrayBuffer ? 0 : value.byteOffset, value instanceof ArrayBuffer ? value.byteLength : value.byteLength);
  const digest = createHash("sha256").update(bytes).digest();
  return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength);
} } }));
afterEach(() => vi.unstubAllGlobals());

describe("volumetric payload loader", () => {
  it("decodes and verifies canonical inline float32 values", async () => {
    const buffer = new ArrayBuffer(8); const view = new DataView(buffer); view.setFloat32(0, 1.25, true); view.setFloat32(4, -2.5, true);
    const hash = await sha256Hex(buffer);
    const payload = { ...payloadBase, encoding: "inline_json", dtype: "float32", inlineValues: [1.25, -2.5], valueCount: 2, uncompressedBytes: 8, logicalSha256: hash } as ValidatedVolumetricPayload;
    const decoded = await loadDecodedVolumetricField({ field, payload, artifacts: [] });
    expect(decoded.byteLength).toBe(8);
    expect(new DataView(decoded.buffer).getFloat32(4, true)).toBe(-2.5);
  });

  it("rejects a logical hash mismatch without returning field bytes", async () => {
    const payload = { ...payloadBase, encoding: "inline_json", dtype: "float32", inlineValues: [1], valueCount: 1, uncompressedBytes: 4, logicalSha256: "0".repeat(64) } as ValidatedVolumetricPayload;
    await expect(loadDecodedVolumetricField({ field, payload, artifacts: [] })).rejects.toMatchObject({ code: "VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH" });
  });
});
