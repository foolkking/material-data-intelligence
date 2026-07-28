import type { Artifact } from "../../lib/planner-api";

export type JsonRecord = Record<string, unknown>;
export type MaterialIntelligenceProductId =
  | "dataset_explorer"
  | "composition_space"
  | "regression"
  | "uncertainty"
  | "classification";
export type MaterialIntelligenceProductState =
  | "PRODUCED"
  | "READY_NOT_RUN"
  | "UNAVAILABLE"
  | "PROFILE_AUTHORITY_UNAVAILABLE"
  | "REJECTED"
  | "STALE"
  | "CAPABILITY_MISMATCH";

export type MaterialDatasetBinding = {
  readonly datasetId: string;
  readonly datasetVersion: string;
  readonly profileId: string;
  readonly profileContractVersion: string;
  readonly semanticHash: string;
  readonly datasetContentHash: string;
  readonly resourceSignature: string;
};

export type MaterialProductAssessment = {
  readonly id: MaterialIntelligenceProductId;
  readonly label: string;
  readonly capability: string;
  readonly state: MaterialIntelligenceProductState;
  readonly reason: string;
  readonly artifact?: Artifact;
  readonly payload?: JsonRecord;
  readonly binding?: MaterialDatasetBinding;
};

export type MaterialIntelligenceAssessment = {
  readonly authority?: MaterialProductAssessment;
  readonly products: readonly MaterialProductAssessment[];
  readonly hasCompatibleEmbeddedCompositionSpace: boolean;
};

type ProductSpec = {
  readonly id: MaterialIntelligenceProductId;
  readonly label: string;
  readonly capability: string;
  readonly artifactName: string;
  readonly schema: string;
  readonly artifactType: string;
};

const PRODUCT_SPECS: readonly ProductSpec[] = [
  { id: "dataset_explorer", label: "Dataset Explorer", capability: "dataset_materials_explorer", artifactName: "dataset_materials_explorer.json", schema: "phase10k2.dataset_materials_explorer.v1", artifactType: "dataset.materials_explorer" },
  { id: "composition_space", label: "Composition Space", capability: "composition_space", artifactName: "composition_space.json", schema: "phase10k4.composition_space.v1", artifactType: "dataset.composition_space" },
  { id: "regression", label: "Regression", capability: "regression_evaluation", artifactName: "materials_ml_regression.json", schema: "phase10k3.materials_ml_regression.v1", artifactType: "ml.regression_evaluation" },
  { id: "uncertainty", label: "Uncertainty", capability: "uncertainty_evaluation", artifactName: "materials_ml_uncertainty.json", schema: "phase10k3.materials_ml_uncertainty.v1", artifactType: "ml.uncertainty_evaluation" },
  { id: "classification", label: "Classification", capability: "classification_evaluation", artifactName: "materials_ml_classification.json", schema: "phase10k3.materials_ml_classification.v1", artifactType: "ml.classification_evaluation" },
] as const;

const HASH_PATTERN = /^[a-f0-9]{64}$/i;

export function inspectMaterialIntelligenceArtifacts(
  artifacts: readonly Artifact[],
  validateProduct?: (id: MaterialIntelligenceProductId, payload: JsonRecord) => string | null,
): MaterialIntelligenceAssessment {
  const candidates = PRODUCT_SPECS.map((spec) => assessCandidate(spec, artifacts, validateProduct));
  const authority = candidates.find((item) => item.id === "dataset_explorer" && item.state === "PRODUCED");
  const available = new Set<string>();
  const unavailable = new Set<string>();
  if (authority?.payload) {
    for (const item of stringList(record(authority.payload.overview).availableAnalyses)) available.add(item);
    for (const item of stringList(record(authority.payload.overview).unavailableAnalyses)) unavailable.add(item);
  }

  const products = candidates.map((candidate) => {
    if (candidate.id === "dataset_explorer") return candidate;
    if (candidate.artifact && candidate.state === "PRODUCED" && authority?.binding && candidate.binding) {
      const mismatch = materialBindingMismatch(authority.binding, candidate.binding);
      if (mismatch) return { ...candidate, state: "STALE" as const, reason: mismatch };
      if (unavailable.has(candidate.capability) && !available.has(candidate.capability)) {
        return { ...candidate, state: "CAPABILITY_MISMATCH" as const, reason: "MATERIAL_INTELLIGENCE_PROFILE_CAPABILITY_MISMATCH" };
      }
      return candidate;
    }
    if (candidate.artifact) return candidate;
    if (!authority) return { ...candidate, state: "PROFILE_AUTHORITY_UNAVAILABLE" as const, reason: "MATERIAL_INTELLIGENCE_PROFILE_AUTHORITY_UNAVAILABLE" };
    if (available.has(candidate.capability)) return { ...candidate, state: "READY_NOT_RUN" as const, reason: "MATERIAL_INTELLIGENCE_PRODUCT_NOT_RUN" };
    return { ...candidate, state: "UNAVAILABLE" as const, reason: "MATERIAL_INTELLIGENCE_PROFILE_DATA_UNAVAILABLE" };
  });
  const composition = products.find((item) => item.id === "composition_space");
  return {
    authority,
    products,
    hasCompatibleEmbeddedCompositionSpace: Boolean(authority && composition?.state === "PRODUCED"),
  };
}

function assessCandidate(
  spec: ProductSpec,
  artifacts: readonly Artifact[],
  validateProduct?: (id: MaterialIntelligenceProductId, payload: JsonRecord) => string | null,
): MaterialProductAssessment {
  const matching = artifacts.flatMap((artifact) => {
    const payload = artifactPayload(artifact);
    const schemaMatch = payload?.schemaVersion === spec.schema && payload.artifactType === spec.artifactType;
    return schemaMatch || artifact.name === spec.artifactName ? [{ artifact, payload }] : [];
  });
  const base = { id: spec.id, label: spec.label, capability: spec.capability } as const;
  if (!matching.length) return { ...base, state: "UNAVAILABLE", reason: "MATERIAL_INTELLIGENCE_ARTIFACT_NOT_PRODUCED" };
  if (matching.length > 1) return { ...base, state: "REJECTED", reason: "MATERIAL_INTELLIGENCE_DUPLICATE_PRODUCT_ARTIFACT" };
  const { artifact, payload } = matching[0];
  if (!payload) {
    return { ...base, artifact, payload: payload || undefined, state: "REJECTED", reason: "MATERIAL_INTELLIGENCE_PRODUCT_SCHEMA_INVALID" };
  }
  const productError = validateProduct?.(spec.id, payload);
  if (productError) return { ...base, artifact, payload, state: "REJECTED", reason: productError };
  if (payload.schemaVersion !== spec.schema || payload.artifactType !== spec.artifactType) {
    return { ...base, artifact, payload, state: "REJECTED", reason: "MATERIAL_INTELLIGENCE_PRODUCT_SCHEMA_INVALID" };
  }
  const binding = materialDatasetBinding(payload);
  if (!binding) return { ...base, artifact, payload, state: "REJECTED", reason: "MATERIAL_INTELLIGENCE_DATASET_BINDING_INVALID" };
  if (!safeSecurityDeclaration(payload.security)) return { ...base, artifact, payload, binding, state: "REJECTED", reason: "MATERIAL_INTELLIGENCE_SECURITY_DECLARATION_INVALID" };
  return { ...base, artifact, payload, binding, state: "PRODUCED", reason: "MATERIAL_INTELLIGENCE_PRODUCT_BOUND" };
}

export function materialDatasetBinding(payload: JsonRecord | null): MaterialDatasetBinding | null {
  const dataset = record(payload?.dataset);
  const binding: MaterialDatasetBinding = {
    datasetId: safeString(dataset.datasetId),
    datasetVersion: safeString(dataset.datasetVersion),
    profileId: safeString(dataset.profileId),
    profileContractVersion: safeString(dataset.profileContractVersion),
    semanticHash: safeString(dataset.semanticHash),
    datasetContentHash: safeString(dataset.datasetContentHash),
    resourceSignature: resourceBindingSignature(dataset.resourceBindings),
  };
  if (!binding.datasetId || !binding.datasetVersion || !binding.profileId || binding.profileContractVersion !== "2.0" || !HASH_PATTERN.test(binding.semanticHash)) return null;
  if (!HASH_PATTERN.test(binding.datasetContentHash)) return null;
  if (!binding.resourceSignature || binding.resourceSignature === "INVALID") return null;
  return binding;
}

export function materialBindingMismatch(left: MaterialDatasetBinding, right: MaterialDatasetBinding): string | null {
  if (left.datasetId !== right.datasetId) return "MATERIAL_INTELLIGENCE_DATASET_ID_MISMATCH";
  if (left.datasetVersion !== right.datasetVersion) return "MATERIAL_INTELLIGENCE_DATASET_VERSION_MISMATCH";
  if (left.profileId !== right.profileId) return "MATERIAL_INTELLIGENCE_PROFILE_ID_MISMATCH";
  if (left.profileContractVersion !== right.profileContractVersion) return "MATERIAL_INTELLIGENCE_PROFILE_CONTRACT_MISMATCH";
  if (left.semanticHash !== right.semanticHash) return "MATERIAL_INTELLIGENCE_SEMANTIC_HASH_MISMATCH";
  if (left.datasetContentHash !== right.datasetContentHash) return "MATERIAL_INTELLIGENCE_CONTENT_BINDING_MISMATCH";
  if (left.resourceSignature !== right.resourceSignature) return "MATERIAL_INTELLIGENCE_RESOURCE_BINDING_MISMATCH";
  return null;
}

export function canonicalSampleKey(value: JsonRecord): string {
  const objectId = safeString(value.objectId);
  const sampleRef = safeString(value.sampleRef);
  if (objectId && sampleRef) return `${objectId}:${sampleRef}`;
  const supplied = safeString(value.sampleKey);
  if (supplied) return supplied;
  const rowIndex = Number(value.rowIndex);
  return `legacy-unbound:${sampleRef || "sample"}:${Number.isSafeInteger(rowIndex) && rowIndex >= 0 ? rowIndex : "unknown"}`;
}

export function artifactPayload(artifact?: Artifact): JsonRecord | null {
  if (!artifact) return null;
  const metadata = record(artifact.metadata);
  for (const candidate of [artifact.content, artifact.payload, metadata.content, metadata.payload, metadata.preview]) {
    if (isRecord(candidate)) return candidate;
    if (typeof candidate === "string") {
      try {
        const parsed: unknown = JSON.parse(candidate);
        if (isRecord(parsed)) return parsed;
      } catch {
        // The JSON fallback remains inert and is handled by the owning component.
      }
    }
  }
  return null;
}

function safeSecurityDeclaration(value: unknown): boolean {
  const security = record(value);
  return security.artifactJavaScript === false
    && security.externalUrls === false
    && security.externalAssets === false
    && security.executableContent === false;
}

function resourceBindingSignature(value: unknown): string {
  if (!Array.isArray(value)) return "";
  const rows = value.flatMap((item) => {
    const entry = record(item);
    const objectId = safeString(entry.objectId);
    const objectType = safeString(entry.objectType);
    const objectHash = safeString(entry.objectHash);
    return objectId && objectType && HASH_PATTERN.test(objectHash) ? [`${objectId}\u0000${objectType}\u0000${objectHash}`] : [];
  });
  if (rows.length !== value.length) return "INVALID";
  return rows.sort().join("\u0001");
}

function isRecord(value: unknown): value is JsonRecord { return Boolean(value && typeof value === "object" && !Array.isArray(value)); }
function record(value: unknown): JsonRecord { return isRecord(value) ? value : {}; }
function safeString(value: unknown): string { return typeof value === "string" || typeof value === "number" ? String(value) : ""; }
function stringList(value: unknown): string[] { return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []; }
