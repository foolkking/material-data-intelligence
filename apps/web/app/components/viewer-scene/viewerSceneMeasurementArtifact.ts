import type { PeriodicMeasurementMode } from "./ViewerMeasurementPanel";
import type { ViewerMeasurementResult } from "./viewerSceneMeasurements";
import type { ImageOffset, PeriodicSiteRef, ValidatedRenderScene } from "./viewerSceneRendererTypes";

export type ViewerMeasurementArtifact = Readonly<{
  schema_version: "phase10f23.viewer_measurement.v1";
  scene: Readonly<{ schema_version: ValidatedRenderScene["schemaVersion"]; resource_id: string; formula: string }>;
  measurement: Readonly<{ kind: ViewerMeasurementResult["kind"]; coordinate_mode: PeriodicMeasurementMode; points: readonly PeriodicSiteRef[]; value: number; unit: ViewerMeasurementResult["unit"]; precision: 6 }>;
  viewer_state: Readonly<{ supercell_expansion: ImageOffset; origin_policy: "positive_octant" }>;
  policy: Readonly<{ periodic_identity: "site_index@[image_offset]"; structure_mutated: false; topology_mutated: false; authoritative_chemistry: false }>;
  warnings: readonly string[];
  security: Readonly<{ inert_json: true; artifact_javascript: false; external_urls: false }>;
}>;

export function buildViewerMeasurementArtifact(scene: ValidatedRenderScene, coordinateMode: PeriodicMeasurementMode, refs: readonly PeriodicSiteRef[], result: ViewerMeasurementResult, expansion: ImageOffset = Object.freeze([1,1,1])): ViewerMeasurementArtifact {
  if (refs.length < 2 || refs.length > 4 || refs.some((ref) => !Number.isSafeInteger(ref.siteIndex) || ref.siteIndex < 0 || ref.imageOffset.some((value) => !Number.isSafeInteger(value) || Math.abs(value) > 3)) || !Number.isFinite(result.value)) throw new Error("VIEWER_MEASUREMENT_ARTIFACT_INVALID");
  const points = Object.freeze(refs.map((ref) => Object.freeze({ siteIndex: ref.siteIndex, imageOffset: Object.freeze([...ref.imageOffset]) as PeriodicSiteRef["imageOffset"] })));
  return Object.freeze({
    schema_version: "phase10f23.viewer_measurement.v1",
    scene: Object.freeze({ schema_version: scene.schemaVersion, resource_id: scene.source.resourceId, formula: scene.formula }),
    measurement: Object.freeze({ kind: result.kind, coordinate_mode: coordinateMode, points, value: Number(result.value.toFixed(6)), unit: result.unit, precision: 6 as const }),
    viewer_state: Object.freeze({ supercell_expansion: Object.freeze([...expansion]) as ImageOffset, origin_policy: "positive_octant" }),
    policy: Object.freeze({ periodic_identity: "site_index@[image_offset]", structure_mutated: false, topology_mutated: false, authoritative_chemistry: false }),
    warnings: Object.freeze(coordinateMode === "displayed_positions" ? ["MEASUREMENT_USES_EXPLICIT_DISPLAYED_IMAGES"] : ["MEASUREMENT_USES_BOUNDED_EXACT_MINIMUM_IMAGE"]),
    security: Object.freeze({ inert_json: true, artifact_javascript: false, external_urls: false }),
  });
}
