import { getPlannerArtifactContent, type Artifact } from "../../lib/planner-api";
import {
  artifactChecksum,
  artifactIdentity,
  artifactVersion,
  resolveArtifactRenderer,
  type WorkspaceRendererDescriptor,
} from "./workspace-renderer-registry";

const HASH_PATTERN = /^[a-f0-9]{64}$/i;
const MAX_BUNDLE_ARTIFACTS = 16;
const MAX_DOWNLOAD_BYTES = 64 * 1024 * 1024;
const MAX_JSON_DEPTH = 14;
const FORBIDDEN_KEYS = new Set(["__proto__", "prototype", "constructor"]);

export class WorkspaceArtifactLoadError extends Error {
  constructor(readonly code: string) { super(code); this.name = "WorkspaceArtifactLoadError"; }
}

export type WorkspaceArtifactLoadScope = Readonly<{
  workspaceId: string;
  workspaceRevision: number;
  projectId: string;
  sourceJobId: string;
}>;

export type LoadedWorkspaceArtifact = Readonly<{
  artifact: Artifact;
  descriptor: WorkspaceRendererDescriptor;
  bytes: ArrayBuffer;
  content: unknown;
  cacheKey: string;
}>;

export class WorkspaceArtifactLoader {
  private readonly cache = new Map<string, Promise<LoadedWorkspaceArtifact>>();

  load(artifact: Artifact, scope: WorkspaceArtifactLoadScope, signal?: AbortSignal): Promise<LoadedWorkspaceArtifact> {
    const descriptor = requireDescriptor(artifact);
    const cacheKey = artifactCacheKey(artifact, descriptor, scope);
    const cached = this.cache.get(cacheKey);
    if (cached) return abortable(cached, signal);
    const pending = loadExactArtifact(artifact, descriptor, scope, signal).catch((error) => {
      this.cache.delete(cacheKey);
      throw error;
    });
    this.cache.set(cacheKey, pending);
    return pending;
  }

  async download(artifact: Artifact, scope: WorkspaceArtifactLoadScope, signal?: AbortSignal): Promise<ArrayBuffer> {
    validateArtifactScope(artifact, scope);
    const descriptor = resolveArtifactRenderer(artifact).descriptor;
    const maximumBytes = descriptor?.maximumPayloadBytes ?? MAX_DOWNLOAD_BYTES;
    const bytes = await getPlannerArtifactContent(scope.sourceJobId, artifactIdentity(artifact)!, { signal, maximumBytes });
    const expected = artifactChecksum(artifact)!;
    const actual = await sha256(bytes);
    if (actual !== expected.toLowerCase()) throw new WorkspaceArtifactLoadError("ARTIFACT_INTEGRITY_MISMATCH");
    return bytes;
  }

  async loadBundle(
    selected: Artifact,
    artifacts: readonly Artifact[],
    scope: WorkspaceArtifactLoadScope,
    signal?: AbortSignal,
  ): Promise<readonly Artifact[]> {
    const descriptor = requireDescriptor(selected);
    const selectedToolCall = selected.toolCallId ?? null;
    const candidates = artifacts.filter((item) => {
      if (selectedToolCall && item.toolCallId !== selectedToolCall) return false;
      return descriptor.bundleArtifactTypes.includes(item.type as never);
    });
    if (candidates.length > MAX_BUNDLE_ARTIFACTS) throw new WorkspaceArtifactLoadError("ARTIFACT_BUNDLE_CAP_EXCEEDED");
    const loaded: Artifact[] = [];
    for (const candidate of candidates) {
      if (signal?.aborted) throw new DOMException("Aborted", "AbortError");
      const resolution = resolveArtifactRenderer(candidate);
      if (!resolution.descriptor || ["METADATA_ONLY", "DOWNLOAD_ONLY"].includes(resolution.descriptor.payloadMode)) {
        loaded.push(candidate);
        continue;
      }
      const result = await this.load(candidate, scope, signal);
      loaded.push({ ...candidate, content: result.content, payload: result.content });
    }
    return Object.freeze(loaded);
  }

  clear(): void { this.cache.clear(); }
}

async function loadExactArtifact(
  artifact: Artifact,
  descriptor: WorkspaceRendererDescriptor,
  scope: WorkspaceArtifactLoadScope,
  signal?: AbortSignal,
): Promise<LoadedWorkspaceArtifact> {
  validateArtifactScope(artifact, scope);
  if (["METADATA_ONLY", "DOWNLOAD_ONLY"].includes(descriptor.payloadMode)) throw new WorkspaceArtifactLoadError("ARTIFACT_PAYLOAD_NOT_RENDERABLE");
  const id = artifactIdentity(artifact)!;
  const bytes = await getPlannerArtifactContent(scope.sourceJobId, id, { signal, maximumBytes: descriptor.maximumPayloadBytes });
  const expected = artifactChecksum(artifact)!;
  const actual = await sha256(bytes);
  if (actual !== expected.toLowerCase()) throw new WorkspaceArtifactLoadError("ARTIFACT_INTEGRITY_MISMATCH");
  const content = descriptor.payloadMode === "TEXT" ? decodeText(bytes) : parseBoundedJson(bytes);
  return Object.freeze({ artifact, descriptor, bytes, content, cacheKey: artifactCacheKey(artifact, descriptor, scope) });
}

export function validateArtifactScope(artifact: Artifact, scope: WorkspaceArtifactLoadScope): void {
  const id = artifactIdentity(artifact);
  const checksum = artifactChecksum(artifact);
  if (!id || !/^[A-Za-z0-9_.:-]{1,160}$/.test(id)) throw new WorkspaceArtifactLoadError("ARTIFACT_ID_INVALID");
  if (artifact.jobId !== scope.sourceJobId) throw new WorkspaceArtifactLoadError("ARTIFACT_FOREIGN_JOB");
  const projectId = typeof artifact.metadata?.projectId === "string" ? artifact.metadata.projectId : null;
  if (projectId && projectId !== scope.projectId) throw new WorkspaceArtifactLoadError("ARTIFACT_FOREIGN_PROJECT");
  if (!checksum || !HASH_PATTERN.test(checksum)) throw new WorkspaceArtifactLoadError("ARTIFACT_CHECKSUM_INVALID");
  if (!Number.isSafeInteger(artifact.sizeBytes) || Number(artifact.sizeBytes) <= 0) throw new WorkspaceArtifactLoadError("ARTIFACT_SIZE_INVALID");
}

export function artifactCacheKey(artifact: Artifact, descriptor: WorkspaceRendererDescriptor, scope: WorkspaceArtifactLoadScope): string {
  validateArtifactScope(artifact, scope);
  return [scope.workspaceId, scope.workspaceRevision, artifactIdentity(artifact), artifactChecksum(artifact), artifact.type, artifactVersion(artifact), descriptor.rendererContract, descriptor.rendererVersion].join("\u0000");
}

export function parseBoundedJson(bytes: ArrayBuffer): unknown {
  const text = decodeText(bytes);
  let value: unknown;
  try { value = JSON.parse(text); } catch { throw new WorkspaceArtifactLoadError("ARTIFACT_JSON_INVALID"); }
  validateJsonValue(value, 0, new Set<object>());
  return value;
}

function validateJsonValue(value: unknown, depth: number, seen: Set<object>): void {
  if (depth > MAX_JSON_DEPTH) throw new WorkspaceArtifactLoadError("ARTIFACT_JSON_DEPTH_EXCEEDED");
  if (typeof value === "number" && !Number.isFinite(value)) throw new WorkspaceArtifactLoadError("ARTIFACT_NON_FINITE_NUMERIC");
  if (value === null || typeof value !== "object") return;
  if (seen.has(value)) throw new WorkspaceArtifactLoadError("ARTIFACT_JSON_CYCLIC");
  seen.add(value);
  if (Array.isArray(value)) {
    value.forEach((item) => validateJsonValue(item, depth + 1, seen));
  } else {
    for (const [key, item] of Object.entries(value as Record<string, unknown>)) {
      if (FORBIDDEN_KEYS.has(key)) throw new WorkspaceArtifactLoadError("ARTIFACT_PROTOTYPE_KEY_REJECTED");
      validateJsonValue(item, depth + 1, seen);
    }
  }
  seen.delete(value);
}

function requireDescriptor(artifact: Artifact): WorkspaceRendererDescriptor {
  const resolution = resolveArtifactRenderer(artifact);
  if (!resolution.descriptor) throw new WorkspaceArtifactLoadError(resolution.reason);
  return resolution.descriptor;
}

function decodeText(bytes: ArrayBuffer): string {
  try { return new TextDecoder("utf-8", { fatal: true }).decode(bytes); }
  catch { throw new WorkspaceArtifactLoadError("ARTIFACT_TEXT_ENCODING_INVALID"); }
}

async function sha256(bytes: ArrayBuffer): Promise<string> {
  if (!globalThis.crypto?.subtle) throw new WorkspaceArtifactLoadError("ARTIFACT_CHECKSUM_UNAVAILABLE");
  const hash = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(hash), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function abortable<T>(promise: Promise<T>, signal?: AbortSignal): Promise<T> {
  if (!signal) return promise;
  if (signal.aborted) return Promise.reject(new DOMException("Aborted", "AbortError"));
  return new Promise<T>((resolve, reject) => {
    const abort = () => reject(new DOMException("Aborted", "AbortError"));
    signal.addEventListener("abort", abort, { once: true });
    promise.then(resolve, reject).finally(() => signal.removeEventListener("abort", abort));
  });
}
