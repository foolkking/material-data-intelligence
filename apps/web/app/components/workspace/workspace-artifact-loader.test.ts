import { createHash } from "node:crypto";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getPlannerArtifactContent, type Artifact } from "../../lib/planner-api";
import { WorkspaceArtifactLoader, WorkspaceArtifactLoadError, artifactCacheKey, parseBoundedJson } from "./workspace-artifact-loader";
import { resolveArtifactRenderer } from "./workspace-renderer-registry";

vi.mock("../../lib/planner-api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../lib/planner-api")>();
  return { ...actual, getPlannerArtifactContent: vi.fn() };
});

const contentMock = vi.mocked(getPlannerArtifactContent);
const scope = { workspaceId: "workspace_1", workspaceRevision: 3, projectId: "project_1", sourceJobId: "job_1" };

beforeEach(() => {
  contentMock.mockReset();
  vi.stubGlobal("crypto", { subtle: { digest: async (_algorithm: string, value: BufferSource) => {
    const bytes = ArrayBuffer.isView(value) ? new Uint8Array(value.buffer, value.byteOffset, value.byteLength) : new Uint8Array(value as ArrayBuffer);
    const digest = createHash("sha256").update(bytes).digest();
    return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength);
  } } });
});

describe("Phase 10M-4 WorkspaceArtifactLoader", () => {
  it("loads active JSON through the authorized API and verifies SHA-256", async () => {
    const bytes = encoded({ rows: [{ objectId: "object_1", value: 2 }] });
    const artifact = fixture(bytes);
    contentMock.mockResolvedValue(bytes);
    const loader = new WorkspaceArtifactLoader();
    const loaded = await loader.load(artifact, scope);
    expect(loaded.content).toEqual({ rows: [{ objectId: "object_1", value: 2 }] });
    expect(contentMock).toHaveBeenCalledWith("job_1", "artifact_1", expect.objectContaining({ maximumBytes: 16 * 1024 * 1024 }));
    await loader.load(artifact, scope);
    expect(contentMock).toHaveBeenCalledTimes(1);
  });

  it("rejects checksum, scope, size and version mismatches before rendering", async () => {
    const bytes = encoded({ value: 1 });
    contentMock.mockResolvedValue(bytes);
    await expect(new WorkspaceArtifactLoader().load({ ...fixture(bytes), sha256: "f".repeat(64) }, scope)).rejects.toMatchObject({ code: "ARTIFACT_INTEGRITY_MISMATCH" });
    expect(() => artifactCacheKey({ ...fixture(bytes), jobId: "foreign" }, descriptor(), scope)).toThrow("ARTIFACT_FOREIGN_JOB");
    expect(() => artifactCacheKey({ ...fixture(bytes), sizeBytes: 0 }, descriptor(), scope)).toThrow("ARTIFACT_SIZE_INVALID");
    expect(() => new WorkspaceArtifactLoader().load({ ...fixture(bytes), version: "2" }, scope)).toThrow("ARTIFACT_CONTRACT_VERSION_UNSUPPORTED");
  });

  it("keeps cache identity bound to revision, checksum and renderer contract", () => {
    const bytes = encoded({ value: 1 });
    const artifact = fixture(bytes);
    const first = artifactCacheKey(artifact, descriptor(), scope);
    const second = artifactCacheKey(artifact, descriptor(), { ...scope, workspaceRevision: 4 });
    expect(first).not.toBe(second);
    expect(first).toContain(descriptor().rendererContract);
    expect(first).toContain(artifact.sha256!);
  });

  it("downloads supported and legacy artifacts only after exact scope and checksum validation", async () => {
    const bytes = encoded({ safe: true });
    const artifact = fixture(bytes);
    contentMock.mockResolvedValue(bytes);
    const loader = new WorkspaceArtifactLoader();
    await expect(loader.download(artifact, scope)).resolves.toEqual(bytes);
    expect(contentMock).toHaveBeenCalledWith("job_1", "artifact_1", expect.objectContaining({ maximumBytes: 16 * 1024 * 1024 }));
    await expect(loader.download({ ...artifact, version: "1.0" }, scope)).resolves.toEqual(bytes);
    await expect(loader.download({ ...artifact, sha256: "f".repeat(64) }, scope)).rejects.toMatchObject({ code: "ARTIFACT_INTEGRITY_MISMATCH" });
  });

  it("rejects deep JSON and prototype keys", () => {
    const deep = encoded(JSON.parse(`${"{\"a\":".repeat(16)}null${"}".repeat(16)}`));
    expect(() => parseBoundedJson(deep)).toThrow("ARTIFACT_JSON_DEPTH_EXCEEDED");
    expect(() => parseBoundedJson(new TextEncoder().encode('{"__proto__":{"x":1}}').buffer)).toThrow("ARTIFACT_PROTOTYPE_KEY_REJECTED");
    expect(new WorkspaceArtifactLoadError("CAP_EXCEEDED").code).toBe("CAP_EXCEEDED");
  });
});

function encoded(value: unknown): ArrayBuffer { return new TextEncoder().encode(JSON.stringify(value)).buffer; }
function fixture(bytes: ArrayBuffer): Artifact { return { id: "artifact_1", artifactId: "artifact_1", jobId: "job_1", type: "metrics_json", version: "1", name: "metrics.json", sizeBytes: bytes.byteLength, contentType: "application/json", sha256: createHash("sha256").update(new Uint8Array(bytes)).digest("hex"), metadata: { projectId: "project_1" } }; }
function descriptor() { return resolveArtifactRenderer({ type: "metrics_json", version: "1" }).descriptor!; }
