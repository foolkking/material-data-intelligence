import { describe, expect, it } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import {
  WORKSPACE_ARTIFACT_TYPES,
  WORKSPACE_RENDERER_REGISTRY,
  resolveArtifactRenderer,
  resolveLoadedArtifactRenderer,
} from "./workspace-renderer-registry";

describe("Phase 10M-4 typed renderer registry", () => {
  it("covers every checked-in Artifact contract exactly once", () => {
    expect(WORKSPACE_ARTIFACT_TYPES).toHaveLength(42);
    expect(WORKSPACE_RENDERER_REGISTRY).toHaveLength(42);
    expect(new Set(WORKSPACE_RENDERER_REGISTRY.map((item) => `${item.artifactType}:${item.artifactVersion}`)).size).toBe(42);
    expect(WORKSPACE_RENDERER_REGISTRY.every((item) => item.lazyPolicy === "ACTIVE_ONLY")).toBe(true);
  });

  it("resolves only exact type and version and never guesses from filename or MIME", () => {
    expect(resolveArtifactRenderer(artifact({ type: "structure_json" })).descriptor?.component).toBe("STRUCTURE");
    expect(resolveArtifactRenderer(artifact({ type: "structure_json", version: "2" })).status).toBe("ARTIFACT_CONTRACT_VERSION_UNSUPPORTED");
    expect(resolveArtifactRenderer(artifact({ type: "unknown", name: "structure.json", contentType: "application/json" })).status).toBe("CONTRACT_UNSUPPORTED");
    expect(resolveArtifactRenderer(artifact({ type: "report_html" })).descriptor?.classification).toBe("INERT_FALLBACK");
  });

  it("adapts table_json only after an exact embedded product contract validates", () => {
    const base = artifact({ type: "table_json", content: { schemaVersion: "wrong", artifactType: "dataset.materials_explorer" } });
    expect(resolveLoadedArtifactRenderer(base).descriptor?.component).toBe("GENERIC_TABLE");
    const exact = artifact({ type: "table_json", content: { schemaVersion: "phase10k2.dataset_materials_explorer.v1", artifactType: "dataset.materials_explorer" } });
    expect(resolveLoadedArtifactRenderer(exact).descriptor?.component).toBe("DATASET");
    const coordination = artifact({ type: "table_json", content: { schema_version: "phase10n1.crystalnn_coordination.v1", artifactType: "structure.coordination_crystalnn" } });
    expect(resolveLoadedArtifactRenderer(coordination).descriptor).toMatchObject({ component: "COORDINATION", heavy: false, accessibilityFallback: "TABLE" });
    const wrongAlgorithm = artifact({ type: "table_json", content: { schema_version: "phase10n1.crystalnn_coordination.v1", artifactType: "structure.coordination_voronoinn" } });
    expect(resolveLoadedArtifactRenderer(wrongAlgorithm).descriptor?.component).toBe("GENERIC_TABLE");
    const localEnvironment = artifact({ type: "table_json", content: { schema_version: "phase10n2.local_environment_polyhedra.v1", artifactType: "structure.local_environment_polyhedra" } });
    expect(resolveLoadedArtifactRenderer(localEnvironment).descriptor).toMatchObject({ component: "LOCAL_ENVIRONMENT", accessibilityFallback: "TABLE" });
    const experimentalXrd = artifact({ type: "table_json", content: { schema_version: "phase10n3.experimental_xrd_comparison.v1", artifactType: "structure.experimental_xrd_comparison" } });
    expect(resolveLoadedArtifactRenderer(experimentalXrd).descriptor).toMatchObject({ component: "EXPERIMENTAL_XRD", accessibilityFallback: "TABLE" });
  });

  it("declares bounded heavy viewers and inert accessibility fallbacks", () => {
    const heavy = WORKSPACE_RENDERER_REGISTRY.filter((item) => item.heavy);
    expect(heavy.length).toBeGreaterThan(0);
    expect(heavy.every((item) => item.payloadMode === "BUNDLE" || item.artifactType === "structure_json")).toBe(true);
    expect(WORKSPACE_RENDERER_REGISTRY.every((item) => ["TABLE", "TEXT_SUMMARY", "METADATA"].includes(item.accessibilityFallback))).toBe(true);
  });
});

function artifact(overrides: Partial<Artifact> = {}): Artifact {
  return { id: "artifact_1", artifactId: "artifact_1", jobId: "job_1", type: "metrics_json", version: "1", name: "metrics.json", sizeBytes: 2, sha256: "a".repeat(64), metadata: { projectId: "project_1" }, ...overrides };
}
