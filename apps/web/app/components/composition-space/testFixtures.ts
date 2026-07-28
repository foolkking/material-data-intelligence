import type { Artifact } from "../../lib/planner-api";

export function compositionSpacePayload() {
  const points = [
    point("s1", 0, "Si", "Si", [0.8, -0.2], 0, { Si: 1 }, 1.1, 0.1),
    point("s2", 1, "NaCl", "Cl-Na", [-0.4, 0.7], 1, { Na: 0.5, Cl: 0.5 }, 2.4, 0.6),
    point("s3", 2, "Li2O", "Li-O", [-0.5, -0.5], 1, { Li: 2 / 3, O: 1 / 3 }, 3.2, 0.3),
  ];
  return {
    schemaVersion: "phase10k4.composition_space.v1",
    artifactType: "dataset.composition_space",
    dataset: { datasetId: "materials", datasetVersion: 1, profileId: "profile_materials_v2", profileContractVersion: "2.0", semanticHash: "a".repeat(64), datasetContentHash: "b".repeat(64) },
    coverage: { selectedRows: 4, validCompositionSamples: 3, invalidCompositionSamples: 1, invalidExamples: [{ objectId: "obj_table", rowIndex: 3, reason: "invalid_formula" }], invalidExamplesTruncated: false, silentDrops: false },
    featureRepresentation: { type: "normalized_atomic_fraction", elementBasis: ["Li", "O", "Na", "Si", "Cl"], basisOrder: "atomic_number_ascending", normalization: "element_amount_divided_by_total_amount", missingElementValue: 0, fractionalOccupancySupported: true, featureDimensions: 5, parser: "pymatgen.core.Composition via application composition semantics" },
    projection: { method: "PCA", dimensions: 2, centering: true, scaling: "none", solver: "sklearn_full_svd", signConvention: "largest_absolute_loading_is_positive", rank: 2, components: [[0, 0, 0, 1, 0], [1, 0, 0, 0, -1]], explainedVarianceRatio: [0.7, 0.25], cumulativeExplainedVarianceRatio: 0.95, mean: [0.2, 0.1, 0.1, 0.3, 0.3] },
    clustering: { status: "READY", method: "kmeans_lloyd", featureSpace: "normalized_atomic_fraction", parameters: { nClusters: 2, randomState: 0, nInit: 10, maxIterations: 300, tolerance: 0.0001, labelOrdering: "centroid_lexicographic" }, clusters: [
      { cluster: 0, sampleCount: 1, dominantElements: [{ element: "Si", meanFraction: 1 }], topChemicalSystems: [{ chemicalSystem: "Si", count: 1 }] },
      { cluster: 1, sampleCount: 2, dominantElements: [{ element: "Li", meanFraction: 1 / 3 }, { element: "Na", meanFraction: 0.25 }], topChemicalSystems: [{ chemicalSystem: "Cl-Na", count: 1 }, { chemicalSystem: "Li-O", count: 1 }] },
    ], scientificAuthority: "descriptive_composition_clusters_not_material_families" },
    comparison: { status: "READY", mode: "group", groups: [{ group: "train", sampleCount: 2 }, { group: "test", sampleCount: 1 }], projectionPolicy: "exploratory_combined_projection", sharedElementBasis: true, sharedPcaFit: true, trainingSafetyClaimed: false },
    coloring: { available: [
      { id: "cluster", kind: "categorical", label: "Composition cluster", source: "composition_space" },
      { id: "chemical_system", kind: "categorical", label: "Chemical system", source: "composition_semantics" },
      { id: "group", kind: "categorical", label: "Dataset / group", source: "explicit_comparison_binding" },
      { id: "property:band_gap", kind: "continuous", label: "band_gap", unit: "eV", source: "material_data_profile_2_material_property" },
      { id: "ml:regression:model:absolute_error", kind: "continuous", label: "regression:model:absolute_error", unit: null, source: "phase10k3_sample_bound_artifact" },
    ], default: "cluster", scientificAuthority: "descriptive_visual_encoding_only" },
    points,
    displayPointKeys: points.map((item) => item.sampleKey),
    displaySampleRefs: points.map((item) => item.sampleRef),
    outlierCandidates: [{ rank: 1, sampleRef: "s2", objectId: "obj_table", rowIndex: 1, distance: 0.72, policy: "euclidean_distance_to_combined_feature_centroid", interpretation: "composition_space_candidate_not_invalid_material" }],
    semantics: { source: "material_data_profile_2", roleInferenceRepeated: false, sampleIdentityPreserved: true, projectionIsNotCanonicalMaterialIdentity: true, clusterMeaning: "composition_cluster_only", outlierMeaning: "distance_to_feature_centroid_candidate_only", structuralSimilarityClaimed: false, chemicalFamilyClaimed: false },
    limits: { maxRows: 100000, maxAnalyzedSamples: 20000, maxElements: 118, maxClusters: 12, maxPlotPoints: 10000, maxOutlierRows: 200, maxColorProperties: 16, maxWarnings: 128, maxArtifactBytes: 16000000 },
    security: { artifactJavaScript: false, externalUrls: false, externalAssets: false, executableContent: false },
    warnings: ["COMPOSITION_PROJECTION_IS_EXPLORATORY"],
  };
}
export function compositionSpaceArtifact(content: unknown = compositionSpacePayload()): Artifact {
  return { artifactId: "artifact_composition_space", id: "artifact_composition_space", name: "composition_space.json", type: "table_json", content };
}

function point(sampleRef: string, rowIndex: number, formula: string, chemicalSystem: string, coordinates: [number, number], cluster: number, elementFractions: Record<string, number>, bandGap: number, absoluteError: number) {
  return {
    sampleKey: `obj_table:${sampleRef}`,
    sampleRef,
    identitySource: "explicit_column",
    objectId: "obj_table",
    rowIndex,
    formula,
    reducedFormula: formula,
    chemicalSystem,
    group: rowIndex < 2 ? "train" : "test",
    coordinates,
    cluster,
    elementFractions,
    propertyValues: { band_gap: bandGap },
    mlValues: { "regression:model:absolute_error": absoluteError },
  };
}
