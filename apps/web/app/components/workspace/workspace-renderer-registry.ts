import type { Artifact } from "../../lib/planner-api";
import type { WorkspaceSelectionKind } from "../../lib/workspace-api";

export const WORKSPACE_ARTIFACT_TYPES = [
  "plotly_json", "plotly_html", "preview_png", "figure_svg", "figure_pdf",
  "matterviz_html", "matterviz_snapshot_png", "structure_json", "trajectory_json",
  "trajectory_summary_json", "trajectory_report_json", "trajectory_manifest_json",
  "phonon_band_json", "phonon_band_dos_json", "phonon_compatibility_json",
  "phonon_dos_json", "phonon_summary_json", "phonon_report_json",
  "phonon_manifest_json", "phonon_animation_json", "phonon_animation_summary_json",
  "phonon_animation_manifest_json", "reciprocal_lattice_json", "brillouin_zone_json",
  "kpath_json", "brillouin_zone_manifest_json", "volumetric_grid_json",
  "volumetric_payload_json", "volumetric_field_json", "volumetric_dataset_json",
  "volumetric_manifest_json", "volumetric_structure_overlay_json", "volumetric_binary",
  "metrics_json", "table_json", "table_csv", "quality_issues_json", "summary_md",
  "report_md", "report_html", "recipe_json", "analysis_plan_json",
] as const;

export type WorkspaceArtifactType = typeof WORKSPACE_ARTIFACT_TYPES[number];
export type RendererClassification =
  | "PRODUCTION_NATIVE_RENDERER"
  | "PRODUCTION_ADAPTED_RENDERER"
  | "CONSUMER_ONLY"
  | "METADATA_ONLY"
  | "INERT_FALLBACK"
  | "UNSUPPORTED";
export type RendererComponent =
  | "GENERIC_PLOT" | "GENERIC_TABLE" | "TEXT" | "JSON" | "STATIC_METADATA"
  | "DATASET" | "ML" | "COMPOSITION" | "STRUCTURE" | "TRAJECTORY"
  | "PHONON_BAND" | "PHONON_DOS" | "PHONON_COMBINED" | "PHONON_ANIMATION"
  | "BRILLOUIN_ZONE" | "VOLUMETRIC" | "COORDINATION" | "DOWNLOAD_ONLY" | "LOCAL_ENVIRONMENT";
export type RendererPayloadMode = "JSON" | "TEXT" | "BUNDLE" | "METADATA_ONLY" | "DOWNLOAD_ONLY";

export type WorkspaceRendererDescriptor = Readonly<{
  artifactType: WorkspaceArtifactType;
  artifactVersion: "1";
  rendererContract: string;
  rendererVersion: "1.0";
  classification: RendererClassification;
  component: RendererComponent;
  payloadMode: RendererPayloadMode;
  heavy: boolean;
  webgl: boolean;
  selectionInputs: readonly WorkspaceSelectionKind[];
  selectionOutputs: readonly WorkspaceSelectionKind[];
  accessibilityFallback: "TABLE" | "TEXT_SUMMARY" | "METADATA";
  maximumPayloadBytes: number;
  maximumRows: number;
  maximumPoints: number;
  lazyPolicy: "ACTIVE_ONLY";
  security: "INERT_VALIDATED_DATA" | "DOWNLOAD_ONLY";
  bundleArtifactTypes: readonly WorkspaceArtifactType[];
}>;

export type RendererResolution = Readonly<{
  status: "SUPPORTED" | "CONTRACT_UNSUPPORTED" | "ARTIFACT_CONTRACT_VERSION_UNSUPPORTED";
  descriptor: WorkspaceRendererDescriptor | null;
  reason: string;
}>;

const JSON_LIMIT = 16 * 1024 * 1024;
const TEXT_LIMIT = 2 * 1024 * 1024;
const BINARY_LIMIT = 64 * 1024 * 1024;
const DATASET_SELECTIONS: readonly WorkspaceSelectionKind[] = ["DATASET_SAMPLE", "MATERIAL_OBJECT", "ARTIFACT"];
const DATASET_OUTPUTS: readonly WorkspaceSelectionKind[] = ["DATASET_SAMPLE", "ARTIFACT"];
const ARTIFACT_SELECTION: readonly WorkspaceSelectionKind[] = ["ARTIFACT"];

function entry(
  artifactType: WorkspaceArtifactType,
  component: RendererComponent,
  options: Partial<Omit<WorkspaceRendererDescriptor, "artifactType" | "artifactVersion" | "rendererContract" | "rendererVersion" | "component">> = {},
): WorkspaceRendererDescriptor {
  const payloadMode = options.payloadMode ?? "JSON";
  return Object.freeze({
    artifactType,
    artifactVersion: "1",
    rendererContract: `workspace.${component.toLowerCase().replaceAll("_", "-")}`,
    rendererVersion: "1.0",
    classification: options.classification ?? "PRODUCTION_ADAPTED_RENDERER",
    component,
    payloadMode,
    heavy: options.heavy ?? false,
    webgl: options.webgl ?? false,
    selectionInputs: Object.freeze([...(options.selectionInputs ?? ARTIFACT_SELECTION)]),
    selectionOutputs: Object.freeze([...(options.selectionOutputs ?? ARTIFACT_SELECTION)]),
    accessibilityFallback: options.accessibilityFallback ?? "TEXT_SUMMARY",
    maximumPayloadBytes: options.maximumPayloadBytes ?? (payloadMode === "TEXT" ? TEXT_LIMIT : JSON_LIMIT),
    maximumRows: options.maximumRows ?? 1_000,
    maximumPoints: options.maximumPoints ?? 100_000,
    lazyPolicy: "ACTIVE_ONLY",
    security: options.security ?? "INERT_VALIDATED_DATA",
    bundleArtifactTypes: Object.freeze([...(options.bundleArtifactTypes ?? [artifactType])]),
  });
}

const TRAJECTORY_BUNDLE = ["trajectory_json", "trajectory_summary_json", "trajectory_report_json", "trajectory_manifest_json"] as const;
const PHONON_BUNDLE = ["phonon_band_json", "phonon_band_dos_json", "phonon_compatibility_json", "phonon_dos_json", "phonon_summary_json", "phonon_report_json", "phonon_manifest_json", "plotly_json", "table_json"] as const;
const ANIMATION_BUNDLE = ["phonon_animation_json", "phonon_animation_summary_json", "phonon_animation_manifest_json"] as const;
const BZ_BUNDLE = ["reciprocal_lattice_json", "brillouin_zone_json", "kpath_json", "brillouin_zone_manifest_json", "summary_md", "recipe_json"] as const;
const VOLUME_BUNDLE = ["volumetric_grid_json", "volumetric_payload_json", "volumetric_field_json", "volumetric_dataset_json", "volumetric_manifest_json", "volumetric_structure_overlay_json", "volumetric_binary", "summary_md", "recipe_json"] as const;

export const WORKSPACE_RENDERER_REGISTRY: readonly WorkspaceRendererDescriptor[] = Object.freeze([
  entry("plotly_json", "GENERIC_PLOT", { accessibilityFallback: "TABLE" }),
  entry("plotly_html", "DOWNLOAD_ONLY", { classification: "INERT_FALLBACK", payloadMode: "DOWNLOAD_ONLY", security: "DOWNLOAD_ONLY", selectionInputs: [], selectionOutputs: [] }),
  entry("preview_png", "STATIC_METADATA", { classification: "METADATA_ONLY", payloadMode: "METADATA_ONLY", selectionOutputs: [] }),
  entry("figure_svg", "DOWNLOAD_ONLY", { classification: "INERT_FALLBACK", payloadMode: "DOWNLOAD_ONLY", security: "DOWNLOAD_ONLY", selectionInputs: [], selectionOutputs: [] }),
  entry("figure_pdf", "STATIC_METADATA", { classification: "METADATA_ONLY", payloadMode: "METADATA_ONLY", selectionOutputs: [] }),
  entry("matterviz_html", "DOWNLOAD_ONLY", { classification: "INERT_FALLBACK", payloadMode: "DOWNLOAD_ONLY", security: "DOWNLOAD_ONLY", selectionInputs: [], selectionOutputs: [] }),
  entry("matterviz_snapshot_png", "STATIC_METADATA", { classification: "METADATA_ONLY", payloadMode: "METADATA_ONLY", selectionOutputs: [] }),
  entry("structure_json", "STRUCTURE", { heavy: true, webgl: true, selectionInputs: ["STRUCTURE", "PERIODIC_SITE", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("trajectory_json", "TRAJECTORY", { payloadMode: "BUNDLE", heavy: true, webgl: true, bundleArtifactTypes: TRAJECTORY_BUNDLE, selectionInputs: ["TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("trajectory_summary_json", "JSON", { bundleArtifactTypes: TRAJECTORY_BUNDLE }),
  entry("trajectory_report_json", "JSON", { bundleArtifactTypes: TRAJECTORY_BUNDLE }),
  entry("trajectory_manifest_json", "JSON", { bundleArtifactTypes: TRAJECTORY_BUNDLE }),
  entry("phonon_band_json", "PHONON_BAND", { payloadMode: "BUNDLE", bundleArtifactTypes: PHONON_BUNDLE, selectionInputs: ["PHONON_Q_POINT", "PHONON_BRANCH", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION, accessibilityFallback: "TABLE" }),
  entry("phonon_band_dos_json", "PHONON_COMBINED", { payloadMode: "BUNDLE", bundleArtifactTypes: PHONON_BUNDLE, selectionInputs: ["PHONON_Q_POINT", "PHONON_BRANCH", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION, accessibilityFallback: "TABLE" }),
  entry("phonon_compatibility_json", "JSON", { bundleArtifactTypes: PHONON_BUNDLE }),
  entry("phonon_dos_json", "PHONON_DOS", { payloadMode: "BUNDLE", bundleArtifactTypes: PHONON_BUNDLE, selectionInputs: ["PHONON_BRANCH", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION, accessibilityFallback: "TABLE" }),
  entry("phonon_summary_json", "JSON", { bundleArtifactTypes: PHONON_BUNDLE }),
  entry("phonon_report_json", "JSON", { bundleArtifactTypes: PHONON_BUNDLE }),
  entry("phonon_manifest_json", "JSON", { bundleArtifactTypes: PHONON_BUNDLE }),
  entry("phonon_animation_json", "PHONON_ANIMATION", { payloadMode: "BUNDLE", heavy: true, webgl: true, bundleArtifactTypes: ANIMATION_BUNDLE }),
  entry("phonon_animation_summary_json", "JSON", { bundleArtifactTypes: ANIMATION_BUNDLE }),
  entry("phonon_animation_manifest_json", "JSON", { bundleArtifactTypes: ANIMATION_BUNDLE }),
  entry("reciprocal_lattice_json", "BRILLOUIN_ZONE", { payloadMode: "BUNDLE", heavy: true, webgl: true, bundleArtifactTypes: BZ_BUNDLE, selectionInputs: ["RECIPROCAL_POINT", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("brillouin_zone_json", "BRILLOUIN_ZONE", { payloadMode: "BUNDLE", heavy: true, webgl: true, bundleArtifactTypes: BZ_BUNDLE, selectionInputs: ["RECIPROCAL_POINT", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("kpath_json", "BRILLOUIN_ZONE", { payloadMode: "BUNDLE", heavy: true, webgl: true, bundleArtifactTypes: BZ_BUNDLE, selectionInputs: ["RECIPROCAL_POINT", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("brillouin_zone_manifest_json", "BRILLOUIN_ZONE", { payloadMode: "BUNDLE", heavy: true, webgl: true, bundleArtifactTypes: BZ_BUNDLE, selectionInputs: ["RECIPROCAL_POINT", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("volumetric_grid_json", "VOLUMETRIC", { payloadMode: "BUNDLE", heavy: true, webgl: true, maximumPayloadBytes: BINARY_LIMIT, bundleArtifactTypes: VOLUME_BUNDLE, selectionInputs: ["VOLUMETRIC_FIELD", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("volumetric_payload_json", "VOLUMETRIC", { payloadMode: "BUNDLE", heavy: true, webgl: true, maximumPayloadBytes: BINARY_LIMIT, bundleArtifactTypes: VOLUME_BUNDLE, selectionInputs: ["VOLUMETRIC_FIELD", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("volumetric_field_json", "VOLUMETRIC", { payloadMode: "BUNDLE", heavy: true, webgl: true, maximumPayloadBytes: BINARY_LIMIT, bundleArtifactTypes: VOLUME_BUNDLE, selectionInputs: ["VOLUMETRIC_FIELD", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("volumetric_dataset_json", "VOLUMETRIC", { payloadMode: "BUNDLE", heavy: true, webgl: true, maximumPayloadBytes: BINARY_LIMIT, bundleArtifactTypes: VOLUME_BUNDLE, selectionInputs: ["VOLUMETRIC_FIELD", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("volumetric_manifest_json", "VOLUMETRIC", { payloadMode: "BUNDLE", heavy: true, webgl: true, maximumPayloadBytes: BINARY_LIMIT, bundleArtifactTypes: VOLUME_BUNDLE, selectionInputs: ["VOLUMETRIC_FIELD", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("volumetric_structure_overlay_json", "VOLUMETRIC", { payloadMode: "BUNDLE", heavy: true, webgl: true, maximumPayloadBytes: BINARY_LIMIT, bundleArtifactTypes: VOLUME_BUNDLE, selectionInputs: ["VOLUMETRIC_FIELD", "ARTIFACT"], selectionOutputs: ARTIFACT_SELECTION }),
  entry("volumetric_binary", "DOWNLOAD_ONLY", { classification: "METADATA_ONLY", payloadMode: "METADATA_ONLY", maximumPayloadBytes: BINARY_LIMIT, selectionOutputs: [] }),
  entry("metrics_json", "GENERIC_TABLE", { accessibilityFallback: "TABLE" }),
  entry("table_json", "GENERIC_TABLE", { selectionInputs: DATASET_SELECTIONS, accessibilityFallback: "TABLE" }),
  entry("table_csv", "DOWNLOAD_ONLY", { classification: "INERT_FALLBACK", payloadMode: "DOWNLOAD_ONLY", security: "DOWNLOAD_ONLY", selectionInputs: [], selectionOutputs: [] }),
  entry("quality_issues_json", "GENERIC_TABLE", { accessibilityFallback: "TABLE" }),
  entry("summary_md", "TEXT", { payloadMode: "TEXT", selectionOutputs: [] }),
  entry("report_md", "TEXT", { payloadMode: "TEXT", selectionOutputs: [] }),
  entry("report_html", "DOWNLOAD_ONLY", { classification: "INERT_FALLBACK", payloadMode: "DOWNLOAD_ONLY", security: "DOWNLOAD_ONLY", selectionInputs: [], selectionOutputs: [] }),
  entry("recipe_json", "JSON", { selectionOutputs: [] }),
  entry("analysis_plan_json", "JSON", { selectionOutputs: [] }),
]);

const BY_CONTRACT = new Map(WORKSPACE_RENDERER_REGISTRY.map((item) => [`${item.artifactType}\u0000${item.artifactVersion}`, item]));
if (BY_CONTRACT.size !== WORKSPACE_RENDERER_REGISTRY.length || WORKSPACE_RENDERER_REGISTRY.length !== WORKSPACE_ARTIFACT_TYPES.length) {
  throw new Error("WORKSPACE_RENDERER_REGISTRY_DUPLICATE_OR_INCOMPLETE");
}

export function resolveArtifactRenderer(artifact: Artifact): RendererResolution {
  if (!WORKSPACE_ARTIFACT_TYPES.includes(artifact.type as WorkspaceArtifactType)) {
    return Object.freeze({ status: "CONTRACT_UNSUPPORTED", descriptor: null, reason: "CONTRACT_UNSUPPORTED" });
  }
  const version = artifactVersion(artifact);
  const descriptor = BY_CONTRACT.get(`${artifact.type}\u0000${version}`) ?? null;
  if (!descriptor) return Object.freeze({ status: "ARTIFACT_CONTRACT_VERSION_UNSUPPORTED", descriptor: null, reason: "ARTIFACT_CONTRACT_VERSION_UNSUPPORTED" });
  return Object.freeze({ status: "SUPPORTED", descriptor, reason: descriptor.classification });
}

export function resolveLoadedArtifactRenderer(artifact: Artifact): RendererResolution {
  const base = resolveArtifactRenderer(artifact);
  if (!base.descriptor || artifact.type !== "table_json") return base;
  const payload = asRecord(artifact.content ?? artifact.payload);
  const schema = typeof payload?.schemaVersion === "string" ? payload.schemaVersion : typeof payload?.schema_version === "string" ? payload.schema_version : "";
  const artifactType = typeof payload?.artifactType === "string" ? payload.artifactType : "";
  const product = PRODUCT_RENDERERS.get(`${schema}\u0000${artifactType}`);
  if (!product) return base;
  return Object.freeze({ status: "SUPPORTED", descriptor: Object.freeze({ ...base.descriptor, ...product }), reason: "STRICT_EMBEDDED_PRODUCT_CONTRACT" });
}

const PRODUCT_RENDERERS = new Map<string, Partial<WorkspaceRendererDescriptor>>([
  ["phase10k2.dataset_materials_explorer.v1\u0000dataset.materials_explorer", { component: "DATASET", rendererContract: "workspace.dataset-materials-explorer", selectionInputs: DATASET_SELECTIONS, selectionOutputs: DATASET_OUTPUTS }],
  ["phase10k4.composition_space.v1\u0000dataset.composition_space", { component: "COMPOSITION", rendererContract: "workspace.composition-space", selectionInputs: DATASET_SELECTIONS, selectionOutputs: DATASET_OUTPUTS }],
  ["phase10k3.materials_ml_regression.v1\u0000ml.regression_evaluation", { component: "ML", rendererContract: "workspace.materials-ml", selectionInputs: DATASET_SELECTIONS, selectionOutputs: ARTIFACT_SELECTION }],
  ["phase10k3.materials_ml_uncertainty.v1\u0000ml.uncertainty_evaluation", { component: "ML", rendererContract: "workspace.materials-ml", selectionInputs: DATASET_SELECTIONS, selectionOutputs: ARTIFACT_SELECTION }],
  ["phase10k3.materials_ml_classification.v1\u0000ml.classification_evaluation", { component: "ML", rendererContract: "workspace.materials-ml", selectionInputs: DATASET_SELECTIONS, selectionOutputs: ARTIFACT_SELECTION }],
  ["phase10n1.crystalnn_coordination.v1\u0000structure.coordination_crystalnn", { component: "COORDINATION", rendererContract: "workspace.coordination", selectionInputs: ["PERIODIC_SITE", "ARTIFACT"], selectionOutputs: ["PERIODIC_SITE", "ARTIFACT"], accessibilityFallback: "TABLE", maximumRows: 50_000 }],
  ["phase10n1.voronoinn_coordination.v1\u0000structure.coordination_voronoinn", { component: "COORDINATION", rendererContract: "workspace.coordination", selectionInputs: ["PERIODIC_SITE", "ARTIFACT"], selectionOutputs: ["PERIODIC_SITE", "ARTIFACT"], accessibilityFallback: "TABLE", maximumRows: 50_000 }],
  ["phase10n2.local_environment_polyhedra.v1\u0000structure.local_environment_polyhedra", { component: "LOCAL_ENVIRONMENT", rendererContract: "workspace.local-environment-polyhedra", selectionInputs: ["PERIODIC_SITE", "LOCAL_ENVIRONMENT", "COORDINATION_POLYHEDRON", "POLYHEDRON_VERTEX", "POLYHEDRON_FACE", "ARTIFACT"], selectionOutputs: ["PERIODIC_SITE", "LOCAL_ENVIRONMENT", "COORDINATION_POLYHEDRON", "POLYHEDRON_VERTEX", "POLYHEDRON_FACE", "ARTIFACT"], accessibilityFallback: "TABLE", maximumRows: 5_000 }],
]);

export function artifactIdentity(artifact: Artifact): string | null { return artifact.artifactId ?? artifact.id ?? null; }
export function artifactChecksum(artifact: Artifact): string | null { return artifact.sha256 ?? artifact.contentHash ?? null; }
export function artifactVersion(artifact: Artifact): string { return typeof artifact.version === "string" ? artifact.version : typeof artifact.metadata?.artifactVersion === "string" ? artifact.metadata.artifactVersion : "1"; }

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null;
}
