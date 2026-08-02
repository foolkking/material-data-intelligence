import type {
  WorkspaceSelectionContext,
  WorkspaceSelectionKind,
  WorkspaceSelectionRef,
} from "../../lib/workspace-api";

export const WORKSPACE_SELECTION_URL_MAX_BYTES = 2_048;
export const WORKSPACE_SELECTION_MAX_SECONDARY = 16;
const WORKSPACE_SELECTION_JSON_MAX_DEPTH = 14;

export const WORKSPACE_SELECTION_KINDS = [
  "DATASET_SAMPLE",
  "MATERIAL_OBJECT",
  "STRUCTURE",
  "PERIODIC_SITE",
  "TRAJECTORY_ATOM",
  "TRAJECTORY_FRAME",
  "PHONON_Q_POINT",
  "PHONON_BRANCH",
  "RECIPROCAL_POINT",
  "VOLUMETRIC_FIELD",
  "ARTIFACT",
  "EVIDENCE_ITEM",
  "CLAIM",
] as const satisfies readonly WorkspaceSelectionKind[];

const KIND_SET = new Set<string>(WORKSPACE_SELECTION_KINDS);
const ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}$/;
const HASH = /^[0-9a-f]{64}$/;
const CONTRACT = /^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$/;
const LOCATOR = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$/;
const FORBIDDEN_KEYS = new Set(["__proto__", "prototype", "constructor"]);

const VALUE_FIELDS = [
  "datasetId", "datasetVersion", "jobId", "objectId", "sampleRef", "structureId",
  "siteId", "trajectoryId", "atomId", "frameId", "phononArtifactId", "qPointId",
  "branchId", "reciprocalArtifactId", "reciprocalPointId", "segmentId", "fieldId",
  "regionId", "artifactId", "artifactChecksum", "artifactContract", "artifactVersion",
  "toolCallId", "bundleId", "bundleHash", "evidenceItemId", "sourceArtifactId",
  "sourceArtifactChecksum", "fieldLocator", "interpretationId", "interpretationHash",
  "claimId",
] as const;

type SelectionValueField = (typeof VALUE_FIELDS)[number];

const REQUIRED: Record<WorkspaceSelectionKind, readonly SelectionValueField[]> = {
  DATASET_SAMPLE: ["datasetId", "datasetVersion", "objectId", "sampleRef"],
  MATERIAL_OBJECT: ["datasetId", "datasetVersion", "objectId"],
  STRUCTURE: ["datasetId", "datasetVersion", "objectId", "structureId"],
  PERIODIC_SITE: ["datasetId", "datasetVersion", "objectId", "structureId", "siteId"],
  TRAJECTORY_ATOM: ["datasetId", "datasetVersion", "trajectoryId", "atomId"],
  TRAJECTORY_FRAME: ["datasetId", "datasetVersion", "trajectoryId", "frameId"],
  PHONON_Q_POINT: ["datasetId", "datasetVersion", "phononArtifactId", "artifactChecksum", "qPointId"],
  PHONON_BRANCH: ["datasetId", "datasetVersion", "phononArtifactId", "artifactChecksum", "branchId"],
  RECIPROCAL_POINT: ["datasetId", "datasetVersion", "reciprocalArtifactId", "artifactChecksum", "reciprocalPointId"],
  VOLUMETRIC_FIELD: ["datasetId", "datasetVersion", "fieldId", "artifactId", "artifactChecksum"],
  ARTIFACT: ["jobId", "artifactId", "artifactChecksum", "artifactContract", "artifactVersion"],
  EVIDENCE_ITEM: ["jobId", "bundleId", "bundleHash", "evidenceItemId", "sourceArtifactId", "sourceArtifactChecksum", "fieldLocator"],
  CLAIM: ["jobId", "interpretationId", "interpretationHash", "claimId"],
};

const ALLOWED: Record<WorkspaceSelectionKind, readonly SelectionValueField[]> = {
  DATASET_SAMPLE: ["datasetId", "datasetVersion", "objectId", "sampleRef", "artifactId", "artifactChecksum"],
  MATERIAL_OBJECT: ["datasetId", "datasetVersion", "objectId", "sampleRef", "artifactId", "artifactChecksum"],
  STRUCTURE: ["datasetId", "datasetVersion", "objectId", "structureId", "artifactId", "artifactChecksum"],
  PERIODIC_SITE: ["datasetId", "datasetVersion", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum"],
  TRAJECTORY_ATOM: ["datasetId", "datasetVersion", "trajectoryId", "atomId", "artifactId", "artifactChecksum"],
  TRAJECTORY_FRAME: ["datasetId", "datasetVersion", "trajectoryId", "frameId", "artifactId", "artifactChecksum"],
  PHONON_Q_POINT: ["datasetId", "datasetVersion", "phononArtifactId", "artifactChecksum", "qPointId", "branchId"],
  PHONON_BRANCH: ["datasetId", "datasetVersion", "phononArtifactId", "artifactChecksum", "branchId", "qPointId"],
  RECIPROCAL_POINT: ["datasetId", "datasetVersion", "reciprocalArtifactId", "artifactChecksum", "reciprocalPointId", "segmentId"],
  VOLUMETRIC_FIELD: ["datasetId", "datasetVersion", "fieldId", "artifactId", "artifactChecksum", "regionId"],
  ARTIFACT: ["jobId", "artifactId", "artifactChecksum", "artifactContract", "artifactVersion", "toolCallId"],
  EVIDENCE_ITEM: ["jobId", "bundleId", "bundleHash", "evidenceItemId", "sourceArtifactId", "sourceArtifactChecksum", "fieldLocator", "claimId"],
  CLAIM: ["jobId", "interpretationId", "interpretationHash", "claimId", "evidenceItemId"],
};

const ID_FIELDS = new Set<SelectionValueField>([
  "datasetId", "jobId", "objectId", "sampleRef", "structureId", "siteId", "trajectoryId",
  "atomId", "frameId", "phononArtifactId", "qPointId", "branchId", "reciprocalArtifactId",
  "reciprocalPointId", "segmentId", "fieldId", "regionId", "artifactId", "toolCallId",
  "bundleId", "evidenceItemId", "sourceArtifactId", "interpretationId", "claimId",
]);
const HASH_FIELDS = new Set<SelectionValueField>([
  "artifactChecksum", "bundleHash", "sourceArtifactChecksum", "interpretationHash",
]);

export type WorkspaceSelectionErrorCode =
  | "SELECTION_SCHEMA_INVALID"
  | "SELECTION_SCOPE_MISMATCH"
  | "SELECTION_DUPLICATE_IDENTITY"
  | "SELECTION_URL_INVALID"
  | "SELECTION_URL_CAP_EXCEEDED";

export class WorkspaceSelectionError extends Error {
  constructor(readonly code: WorkspaceSelectionErrorCode, message: string) {
    super(message);
    this.name = "WorkspaceSelectionError";
  }
}

export function validateWorkspaceSelectionRef(value: unknown): WorkspaceSelectionRef {
  const input = object(value, "selection reference");
  rejectUnknown(input, new Set(["selectionSchemaVersion", "kind", "sourceScopeHash", "projectId", ...VALUE_FIELDS]));
  if (input.selectionSchemaVersion !== "1.0" || typeof input.kind !== "string" || !KIND_SET.has(input.kind)) {
    invalid("Selection reference version or kind is invalid.");
  }
  const kind = input.kind as WorkspaceSelectionKind;
  const sourceScopeHash = exactHash(input.sourceScopeHash, "sourceScopeHash");
  const projectId = exactId(input.projectId, "projectId", 64);
  const normalized: Record<string, unknown> = {
    selectionSchemaVersion: "1.0",
    kind,
    sourceScopeHash,
    projectId,
  };
  for (const field of VALUE_FIELDS) normalized[field] = nullableString(input[field], field);
  for (const field of REQUIRED[kind]) {
    if (!normalized[field]) invalid(`${kind} is missing ${field}.`);
  }
  const allowed = new Set(ALLOWED[kind]);
  for (const field of VALUE_FIELDS) {
    const current = normalized[field];
    if (current !== null && !allowed.has(field)) invalid(`${kind} cannot contain ${field}.`);
    if (current === null) continue;
    if (ID_FIELDS.has(field)) normalized[field] = exactId(current, field, field === "datasetId" || field === "jobId" || field === "toolCallId" ? 64 : 96);
    if (HASH_FIELDS.has(field)) normalized[field] = exactHash(current, field);
  }
  if (normalized.artifactContract !== null && !CONTRACT.test(String(normalized.artifactContract))) invalid("artifactContract is invalid.");
  if (normalized.fieldLocator !== null && !LOCATOR.test(String(normalized.fieldLocator))) invalid("fieldLocator is invalid.");
  if (normalized.datasetVersion !== null && String(normalized.datasetVersion).length > 128) invalid("datasetVersion exceeds its cap.");
  if (normalized.artifactVersion !== null && String(normalized.artifactVersion).length > 64) invalid("artifactVersion exceeds its cap.");
  return normalized as unknown as WorkspaceSelectionRef;
}

export function validateWorkspaceSelectionContext(value: unknown): WorkspaceSelectionContext {
  const input = object(value, "selection context");
  rejectUnknown(input, new Set(["schemaVersion", "sourceScopeHash", "primary", "secondary", "propagation", "compatibility", "cleared"]));
  if (input.schemaVersion !== "1.0" || input.propagation !== "EXACT_COMPATIBLE_ONLY") invalid("Selection context contract is invalid.");
  if (!["EXACT", "NOT_APPLICABLE", "STALE", "UNSUPPORTED"].includes(String(input.compatibility))) invalid("Selection compatibility is invalid.");
  if (typeof input.cleared !== "boolean" || !Array.isArray(input.secondary) || input.secondary.length > WORKSPACE_SELECTION_MAX_SECONDARY) invalid("Selection context bounds are invalid.");
  const sourceScopeHash = exactHash(input.sourceScopeHash, "sourceScopeHash");
  const primary = input.primary === null || input.primary === undefined ? null : validateWorkspaceSelectionRef(input.primary);
  const secondary = input.secondary.map(validateWorkspaceSelectionRef);
  if (input.cleared && (primary || secondary.length)) invalid("A cleared selection cannot retain identities.");
  if (!primary && secondary.length) invalid("Secondary selections require a primary selection.");
  const refs = primary ? [primary, ...secondary] : [];
  if (refs.some((ref) => ref.sourceScopeHash !== sourceScopeHash)) scopeMismatch("Selection source scope hash mismatch.");
  if (primary && secondary.some((ref) => ref.kind !== primary.kind || ref.projectId !== primary.projectId || ref.datasetId !== primary.datasetId || ref.datasetVersion !== primary.datasetVersion)) {
    scopeMismatch("Multi-selection must retain kind, project, dataset, and version.");
  }
  const identities = refs.map(selectionRefIdentity);
  if (new Set(identities).size !== identities.length) throw new WorkspaceSelectionError("SELECTION_DUPLICATE_IDENTITY", "Selection context contains duplicate identities.");
  const context: WorkspaceSelectionContext = {
    schemaVersion: "1.0",
    sourceScopeHash,
    primary,
    secondary,
    propagation: "EXACT_COMPATIBLE_ONLY",
    compatibility: input.compatibility as WorkspaceSelectionContext["compatibility"],
    cleared: input.cleared,
  };
  if (utf8(canonicalSelectionJson(context)).length > 131_072) invalid("Selection context exceeds its serialized cap.");
  return context;
}

export function clearedWorkspaceSelection(sourceScopeHash: string): WorkspaceSelectionContext {
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0", sourceScopeHash, primary: null, secondary: [],
    propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "NOT_APPLICABLE", cleared: true,
  });
}

export function canonicalSelectionJson(value: WorkspaceSelectionContext | WorkspaceSelectionRef): string {
  return JSON.stringify(sortValue(value));
}

export function selectionRefIdentity(value: WorkspaceSelectionRef): string {
  return canonicalSelectionJson(validateWorkspaceSelectionRef(value));
}

export function selectionsEqual(left: WorkspaceSelectionContext | null, right: WorkspaceSelectionContext | null): boolean {
  if (left === null || right === null) return left === right;
  return canonicalSelectionJson(validateWorkspaceSelectionContext(left)) === canonicalSelectionJson(validateWorkspaceSelectionContext(right));
}

export function encodeWorkspaceSelectionUrl(value: WorkspaceSelectionContext): string {
  const bytes = utf8(canonicalSelectionJson(validateWorkspaceSelectionContext(value)));
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  const token = btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/u, "");
  if (utf8(token).length > WORKSPACE_SELECTION_URL_MAX_BYTES) throw new WorkspaceSelectionError("SELECTION_URL_CAP_EXCEEDED", "Selection URL exceeds 2048 bytes.");
  return token;
}

export function decodeWorkspaceSelectionUrl(token: string): WorkspaceSelectionContext {
  if (utf8(token).length > WORKSPACE_SELECTION_URL_MAX_BYTES) throw new WorkspaceSelectionError("SELECTION_URL_CAP_EXCEEDED", "Selection URL exceeds 2048 bytes.");
  if (!/^[A-Za-z0-9_-]+$/u.test(token)) throw new WorkspaceSelectionError("SELECTION_URL_INVALID", "Selection URL is not canonical base64url.");
  try {
    const base64 = token.replaceAll("-", "+").replaceAll("_", "/") + "=".repeat((4 - (token.length % 4)) % 4);
    const binary = atob(base64);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    const raw = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    assertNoDuplicateJsonKeys(raw);
    const parsed = JSON.parse(raw) as unknown;
    const context = validateWorkspaceSelectionContext(parsed);
    if (encodeWorkspaceSelectionUrl(context) !== token) throw new Error("non-canonical");
    return context;
  } catch (error) {
    if (error instanceof WorkspaceSelectionError) throw error;
    throw new WorkspaceSelectionError("SELECTION_URL_INVALID", "Selection URL payload is invalid or non-canonical.");
  }
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value) || Object.getPrototypeOf(value) !== Object.prototype) invalid(`${label} must be a plain object.`);
  return value as Record<string, unknown>;
}

function rejectUnknown(value: Record<string, unknown>, allowed: Set<string>): void {
  for (const key of Object.keys(value)) {
    if (FORBIDDEN_KEYS.has(key) || !allowed.has(key)) invalid(`Unknown or forbidden selection field: ${key}`);
  }
}

function nullableString(value: unknown, field: string): string | null {
  if (value === null || value === undefined) return null;
  if (typeof value !== "string" || value.length === 0 || value.length > 160) invalid(`${field} must be a bounded string.`);
  return value;
}

function exactId(value: unknown, field: string, maxLength = 96): string {
  if (typeof value !== "string" || value.length > maxLength || !ID.test(value)) invalid(`${field} is not an exact identity.`);
  return value;
}

function exactHash(value: unknown, field: string): string {
  if (typeof value !== "string" || !HASH.test(value)) invalid(`${field} is not a SHA-256 identity.`);
  return value;
}

function sortValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortValue);
  if (typeof value === "object" && value !== null) {
    const record = value as Record<string, unknown>;
    return Object.fromEntries(Object.keys(record).sort().map((key) => [key, sortValue(record[key])]));
  }
  return value;
}

function assertNoDuplicateJsonKeys(raw: string): void {
  let offset = 0;
  const whitespace = () => { while (/\s/u.test(raw[offset] || "")) offset += 1; };
  const stringValue = (): string => {
    const start = offset;
    if (raw[offset] !== '"') throw new Error("expected string");
    offset += 1;
    while (offset < raw.length) {
      if (raw[offset] === "\\") { offset += 2; continue; }
      if (raw[offset] === '"') {
        offset += 1;
        return JSON.parse(raw.slice(start, offset)) as string;
      }
      offset += 1;
    }
    throw new Error("unterminated string");
  };
  const value = (depth: number): void => {
    if (depth > WORKSPACE_SELECTION_JSON_MAX_DEPTH) throw new Error("JSON depth exceeded");
    whitespace();
    if (raw[offset] === "{") {
      offset += 1;
      const keys = new Set<string>();
      whitespace();
      if (raw[offset] === "}") { offset += 1; return; }
      while (offset < raw.length) {
        whitespace();
        const key = stringValue();
        if (keys.has(key)) throw new Error("duplicate key");
        keys.add(key);
        whitespace();
        if (raw[offset] !== ":") throw new Error("expected colon");
        offset += 1;
        value(depth + 1);
        whitespace();
        if (raw[offset] === "}") { offset += 1; return; }
        if (raw[offset] !== ",") throw new Error("expected comma");
        offset += 1;
      }
      throw new Error("unterminated object");
    }
    if (raw[offset] === "[") {
      offset += 1;
      whitespace();
      if (raw[offset] === "]") { offset += 1; return; }
      while (offset < raw.length) {
        value(depth + 1);
        whitespace();
        if (raw[offset] === "]") { offset += 1; return; }
        if (raw[offset] !== ",") throw new Error("expected comma");
        offset += 1;
      }
      throw new Error("unterminated array");
    }
    if (raw[offset] === '"') { stringValue(); return; }
    const scalar = raw.slice(offset).match(/^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/u)?.[0];
    if (!scalar) throw new Error("invalid scalar");
    offset += scalar.length;
  };
  value(1);
  whitespace();
  if (offset !== raw.length) throw new Error("trailing JSON");
}

function utf8(value: string): Uint8Array { return new TextEncoder().encode(value); }
function invalid(message: string): never { throw new WorkspaceSelectionError("SELECTION_SCHEMA_INVALID", message); }
function scopeMismatch(message: string): never { throw new WorkspaceSelectionError("SELECTION_SCOPE_MISMATCH", message); }
