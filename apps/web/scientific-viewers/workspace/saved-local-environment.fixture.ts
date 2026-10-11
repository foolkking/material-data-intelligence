import type { Artifact } from "../../app/lib/planner-api";

const HASH = "a".repeat(64);
const STRUCTURE_HASH = "b".repeat(64);

export function localEnvironmentArtifactFixture(): Artifact {
  return {
    id: "artifact_n2", artifactId: "artifact_n2", jobId: "job_demo", toolCallId: "call_n2", type: "table_json", version: "1", contentHash: HASH, sha256: HASH,
    metadata: { projectId: "project_demo" }, content: {
      schema_version: "phase10n2.local_environment_polyhedra.v1", artifactType: "structure.local_environment_polyhedra",
      tool: { toolId: "structure.local_environment_polyhedra", toolVersion: "0.1.0", adapterVersion: "0.1.0" },
      algorithm: { classification: "mdi.angular_spectrum_reference_match@1.0.0", faceConstruction: "scipy.spatial.ConvexHull@1.17.1" },
      referenceCatalog: { catalogId: "mdi.local_geometry_reference_catalog", catalogVersion: "1.0.0", geometryIds: ["tetrahedral"] },
      resolvedParameters: {}, parameterHash: HASH, scope: { sourceResourceId: "structure_resource", sourceResourceHash: HASH, structureHash: STRUCTURE_HASH },
      sourceCoordination: { artifactId: "artifact_n1", artifactChecksum: HASH, toolId: "structure.coordination_crystalnn", toolVersion: "0.1.0", algorithmId: "pymatgen.crystalnn", algorithmVersion: "2026.5.4", parameterHash: HASH, contractVersion: "phase10n1.crystalnn_coordination.v1" },
      coverage: { status: "COMPLETE", requestedSites: 1, evaluatedSites: 1, unavailableSites: 0, classifiedSites: 1, ambiguousSites: 0, unclassifiedSites: 0, ratio: 1 }, warnings: [],
      siteResults: [{ environmentIdentity: "environment:demo", polyhedronIdentity: "polyhedron:demo", siteId: `site:${STRUCTURE_HASH}:0`, siteIndex: 0, structureHash: STRUCTURE_HASH,
        classification: { status: "CLASSIFIED", referenceGeometryId: "tetrahedral", referenceGeometryVersion: "1.0.0", geometryDistanceRms: 0, geometryScore: 1, alternatives: [] },
        sourceCoordinationValue: 4, sourceCoordinationSemantics: "crystalnn_weight_sum", neighborRelationIdentities: ["neighbor:0", "neighbor:1", "neighbor:2", "neighbor:3"],
        polyhedron: { status: "AVAILABLE", unavailableReason: null, vertices: [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]].map((coordinates, index) => ({ vertexIdentity: `vertex:${index}`, neighborIdentity: `neighbor:${index}`, neighborSiteId: `site:${STRUCTURE_HASH}:${index + 1}`, periodicImage: [0, 0, 0], relativeCartesian: coordinates, distance: Math.sqrt(3), distanceUnit: "angstrom" })), faces: [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]].map((indices, index) => ({ faceIdentity: `face:${index}`, vertexIdentities: indices.map((vertex) => `vertex:${vertex}`) })) },
        distortionMetrics: { geometryDistanceRms: 0, radialDistanceMean: 2.3 }, warnings: [],
      }],
      runtimeDiagnostics: {}, provenance: {}, limits: {}, security: {},
    },
  };
}
