import { describe, expect, it } from "vitest";

import { validateViewerSceneForRenderer } from "./viewer-scene/viewerSceneRendererValidation";
import {
  projectElectronicSource,
  projectVolumetricSourceSummary,
  sourceResourceArtifact,
  sourceResourceArtifacts,
  projectVolumetricSourceArtifacts,
  normalizeResultArtifactForViewer,
} from "./ScientificViewerAdapter";
import { validateVolumetricArtifacts } from "./volumetric-viewer/volumetricValidation";
import { buildElectrostaticPotentialProduct, potentialGaugeView, planarProfiles } from "../../scientific-viewers/volumetric-viewer/electrostaticPotentialProduct";

function sourcePreviewFixture() {
  const resource = { objectId: "preview-source", objectType: "Structure", datasetId: "dataset", versionId: "v1", objectHash: "a".repeat(64), payload: {
    lattice: { matrix: [[4, 0, 0], [0, 4, 0], [0, 0, 4]] },
    sites: [
      { species: [{ element: "Si", occu: 1 }], xyz: [0, 0, 0], abc: [0, 0, 0] },
      { species: [{ element: "Si", occu: 1 }], xyz: [1, 0, 0], abc: [0.25, 0, 0] },
    ],
  } };
  const original = sourceResourceArtifact(resource).content as Record<string, unknown> & { scene: Record<string, unknown> };
  const scene = { ...original, provenance: { projection: "source_structure_preview/1.0", source_hash: resource.objectHash,
    source_object_id: resource.objectId, source_dataset_id: resource.datasetId, source_version_id: resource.versionId } as Record<string, string>,
    scene: { ...original.scene, bonds: [{ id: "bond:0:0,0,0->1:0,0,0", from: { site_index: 0, image_offset: [0, 0, 0] },
      to: { site_index: 1, image_offset: [0, 0, 0] }, displacement_cartesian: [1, 0, 0], distance_angstrom: 1,
      source: "distance_cutoff", authoritative: false }] },
  };
  return { resource, scene };
}

describe("sourceResourceArtifact", () => {
  it("uses a validated server preview only for its exact source identity", () => {
    const { resource, scene } = sourcePreviewFixture();
    const before = JSON.stringify(resource.payload);
    const artifact = sourceResourceArtifact({ ...resource, viewerScene: scene });
    expect(artifact.content).toBe(scene);
    expect(artifact).toMatchObject({ artifactId: "source:preview-source", sha256: resource.objectHash, metadata: { sourceVersionId: "v1" } });
    expect(JSON.stringify(resource.payload)).toBe(before);
    expect(validateViewerSceneForRenderer(artifact.content).valid).toBe(true);
  });

  it.each(["source_hash", "source_object_id", "source_dataset_id", "source_version_id", "projection"])(
    "does not adopt a connection preview with a conflicting %s", field => {
      const { resource, scene } = sourcePreviewFixture();
      scene.provenance[field] = "different";
      const artifact = sourceResourceArtifact({ ...resource, viewerScene: scene });
      expect(artifact.content).not.toBe(scene);
      expect(artifact.content).toMatchObject({ scene: { bonds: [] } });
    },
  );

  it("rejects invalid connection geometry even when source identifiers match", () => {
    const { resource, scene } = sourcePreviewFixture();
    scene.scene.bonds[0].distance_angstrom = 5;
    const artifact = sourceResourceArtifact({ ...resource, viewerScene: scene });
    expect(artifact.content).toMatchObject({ scene: { bonds: [] } });
  });

  it("retains the original atom preview and a readable reason when the connection search is bounded out", () => {
    const { resource } = sourcePreviewFixture();
    const artifact = sourceResourceArtifact({ ...resource, viewerSceneIssue: "VIEWER_NEIGHBOR_WORK_LIMIT" });
    expect(artifact.content).toMatchObject({
      scene: { sites: expect.arrayContaining([expect.objectContaining({ xyz: [1, 0, 0] })]), bonds: [] },
      warnings: expect.arrayContaining([expect.objectContaining({ code: "VIEWER_PREVIEW_CONNECTIONS_UNAVAILABLE", message: expect.stringContaining("近邻搜索超出快速预览范围") })]),
    });
  });

  it("keeps the explicitly selected source version authoritative over a refreshed inventory", () => {
    const selected = { objectId: "table", objectType: "DataFrame", datasetId: "dataset", versionId: "v1", objectHash: "a".repeat(64), payload: [{ measured: 1 }] };
    const newer = { ...selected, versionId: "v2", objectHash: "b".repeat(64), payload: [{ measured: 2 }] };
    const artifacts = sourceResourceArtifacts(selected, [newer]);
    expect(artifacts).toHaveLength(1);
    expect(artifacts[0]).toMatchObject({ sha256: selected.objectHash, content: { rows: [{ measured: 1 }] }, metadata: { sourceVersionId: "v1" } });
  });

  it("renders the selected volume's field values when an earlier volume exists in the dataset", () => {
    const volume = (objectId: string, value: number) => ({ objectId, objectType: "VolumetricData", datasetId: "dataset", payload: {
      source_format: "gaussian_cube", source_name: `${objectId}.cube`, shape: [2, 2, 2], origin_cartesian: [0, 0, 0], step_matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
      boundary_conditions: ["non_periodic", "non_periodic", "non_periodic"], endpoint_policy: "not_applicable", sample_location: "node",
      channels: [{ name: objectId, quantity: "generic_scalar", canonical_unit: "dimensionless", values: Array(8).fill(value) }],
    } });
    const first = volume("first", 1), selected = volume("second", 2);
    const artifacts = sourceResourceArtifacts(selected, [first, selected]);
    const result = validateVolumetricArtifacts(artifacts.find(item => item.type === "volumetric_dataset_json")?.content,
      artifacts.find(item => item.type === "volumetric_manifest_json")?.content);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.bundle.fields[0].field).toMatchObject({ fieldName: "second", minimum: 2, maximum: 2 });
    expect(artifacts.every(item => item.metadata?.sourceObjectId === "second")).toBe(true);
  });

  it("keeps ambiguous companion resources individually accessible instead of choosing the first", () => {
    const selected = { objectId: "band", objectType: "PhononBand", datasetId: "dataset", payload: {} };
    const dos = { objectId: "dos", objectType: "PhononDos", datasetId: "dataset", payload: {} };
    expect(sourceResourceArtifacts(selected, [selected, dos, { ...dos, objectId: "other-dos" }]).map(item => item.artifactId)).toEqual(["source:band"]);
    expect(sourceResourceArtifacts(dos, [selected, dos, { ...dos, objectId: "other-dos" }]).map(item => item.artifactId)).toEqual(["source:dos", "source:band"]);
  });

  it("keeps structure summaries in the structured preview instead of the 3D scene renderer", () => {
    const normalized = normalizeResultArtifactForViewer({
      artifactId: "summary-1",
      id: "summary-1",
      type: "structure_json",
      version: "1",
      name: "structure_summary.json",
      metadata: { toolId: "structure.summary" },
      content: { rows: [{ property: "formula", value: "Ca5P3O13" }] },
    } as never);
    expect(normalized.type).toBe("table_json");
    expect(normalized.content).toMatchObject({ rows: [{ property: "formula" }] });
  });

  it("turns unregistered structured result objects into a readable table summary", () => {
    const normalized = normalizeResultArtifactForViewer({
      artifactId: "composition-1",
      id: "composition-1",
      type: "table_json",
      version: "1",
      name: "structure_composition",
      content: { artifactType: "structure.composition_from_structure", structureCount: 1, elementCounts: { Ca: 10 } },
    } as never);
    expect(normalized.content).toMatchObject({ rows: expect.arrayContaining([{ property: "artifactType", value: "structure.composition_from_structure" }]) });
  });

  it("projects experimental XRD data as one bounded scientific series", () => {
    const artifact = sourceResourceArtifact({
      objectId: "xrd-1",
      objectType: "DataFrame",
      objectHash: "hash-1",
      datasetId: "dataset-1",
      payload: {
        twoTheta: [20, 21, 22],
        intensity: [0.1, 1, 0.2],
      },
    });

    expect(artifact.type).toBe("plotly_json");
    expect(artifact.name).toBe("实验 XRD 图谱");
    expect(artifact.content).toMatchObject({
      figure: {
        data: [{ type: "scattergl", mode: "lines", x: [20, 21, 22], y: [0.1, 1, 0.2] }],
        layout: { xaxis: { title: { text: "2θ (°)" } } },
      },
    });
  });

  it("reuses the structure renderer for non-periodic Atoms resources", () => {
    const artifact = sourceResourceArtifact({
      objectId: "atoms-1",
      objectType: "Atoms",
      datasetId: "dataset-1",
      payload: { symbols: ["H", "H"], positions: [[0, 0, 0], [0, 0, 0.74]] },
    });

    expect(artifact.type).toBe("structure_json");
    expect(artifact.name).toBe("原子结构");
    expect(validateViewerSceneForRenderer(artifact.content)).toEqual(expect.objectContaining({ valid: true, errors: [] }));
    expect(artifact.content).toMatchObject({
      metadata: { formula: "H2", periodic: false, site_count: 2 },
      scene: { lattice: { pbc: [false, false, false], presentation_only: true }, bonds: [] },
      provenance: { presentation_cell_is_scientific_authority: false },
    });
  });

  it("projects a normalized periodic Structure into the validated inert viewer scene", () => {
    const artifact = sourceResourceArtifact({
      objectId: "structure-1",
      objectType: "Structure",
      objectHash: "a".repeat(64),
      datasetId: "dataset-1",
      payload: {
        lattice: { matrix: [[4, 0, 0], [0, 4, 0], [0, 0, 4]] },
        sites: [
          { label: "Ba1", species: [{ element: "Ba", occu: 1 }], abc: [0, 0, 0], xyz: [0, 0, 0] },
          { label: "Ti1", species: [{ element: "Ti", occu: 1 }], abc: [0.5, 0.5, 0.5], xyz: [2, 2, 2] },
        ],
      },
    });

    expect(artifact.type).toBe("structure_json");
    expect(validateViewerSceneForRenderer(artifact.content)).toEqual(expect.objectContaining({ valid: true, errors: [] }));
    expect(artifact.content).toMatchObject({ metadata: { formula: "BaTi", site_count: 2 }, scene: { bonds: [] } });
  });

  it("projects exact electronic source values into the existing band and DOS display contracts", () => {
    const band = {
      objectId: "band-1", objectType: "ElectronicBand", objectHash: "b".repeat(64), datasetId: "dataset-1",
      payload: {
        schemaVersion: "phase10n5.electronic_band_resource.v1", resourceId: "band-resource", resourceVersion: "1", resourceHash: "b".repeat(64),
        calculationIdentity: "calc-1", structureIdentity: "structure-1", energyUnit: "eV", energyReference: "fermi", fermiEnergyEv: 0, spinMode: "non_spin_polarized",
        kpoints: [{ kpointId: "k-0", fractionalCoordinates: [0, 0, 0] }, { kpointId: "k-1", fractionalCoordinates: [0.5, 0, 0] }], pathSegments: [],
        bands: [{ bandId: "v-1", spinChannel: "none", energiesEv: [-1, -0.8], occupations: [1, 1] }],
      },
    } as const;
    const dos = {
      objectId: "dos-1", objectType: "ElectronicDos", objectHash: "c".repeat(64), datasetId: "dataset-1",
      payload: {
        schemaVersion: "phase10n5.electronic_dos_resource.v1", resourceId: "dos-resource", resourceVersion: "1", resourceHash: "c".repeat(64),
        calculationIdentity: "calc-1", structureIdentity: "structure-1", energyUnit: "eV", energyReference: "fermi", fermiEnergyEv: 0, spinMode: "non_spin_polarized",
        energiesEv: [-1, 0, 1], totalDos: [{ channelId: "total", spinChannel: "none", label: "总 DOS", values: [0.2, 1, 0.3] }], projections: [],
        projectionCompleteness: "total_only", dosUnitSemantic: "states_per_electron_volt",
      },
    } as const;

    const bandProjection = projectElectronicSource(band);
    const dosProjection = projectElectronicSource(dos);
    const artifacts = sourceResourceArtifacts(band, [band, dos]);

    expect(bandProjection).toMatchObject({ artifactType: "electronic.band_structure", schemaVersion: "phase10n5.electronic_band_structure.v1", gap: { status: "UNAVAILABLE", valueEv: null }, coverage: { kpointCount: 2, bandCount: 1, stateCount: 2 } });
    expect(dosProjection).toMatchObject({ artifactType: "electronic.dos", schemaVersion: "phase10n5.electronic_dos.v1", energyPointIds: ["source-dos-point:dos-1:0", "source-dos-point:dos-1:1", "source-dos-point:dos-1:2"], coverage: { energyPointCount: 3, totalChannelCount: 1 } });
    expect(artifacts.map((artifact) => artifact.type)).toEqual(["electronic_band_json", "electronic_dos_json"]);
  });

  it("keeps phonon band and DOS source contracts together without fabricating a derived combined artifact", () => {
    const band = { objectId: "phonon-band", objectType: "PhononBand", datasetId: "dataset-2", payload: { schema_version: "phase10h.phonon_band.v1" } };
    const dos = { objectId: "phonon-dos", objectType: "PhononDos", datasetId: "dataset-2", payload: { schema_version: "phase10h.phonon_dos.v1" } };

    const artifacts = sourceResourceArtifacts(band, [band, dos]);

    expect(artifacts.map((artifact) => artifact.type)).toEqual(["phonon_band_json", "phonon_dos_json"]);
    expect(artifacts.some((artifact) => artifact.type === "phonon_band_dos_json")).toBe(false);
  });

  it("bundles experimental XRD with a real companion structure", () => {
    const xrd = { objectId: "xrd", objectType: "DataFrame", datasetId: "dataset-3", payload: { twoTheta: [20, 21], intensity: [0.2, 1] } };
    const structure = { objectId: "structure", objectType: "Structure", datasetId: "dataset-3", payload: { lattice: { matrix: [[4, 0, 0], [0, 4, 0], [0, 0, 4]] }, sites: [{ label: "Si1", species: [{ element: "Si" }], xyz: [0, 0, 0], abc: [0, 0, 0] }] } };

    expect(sourceResourceArtifacts(xrd, [xrd, structure]).map((artifact) => artifact.type)).toEqual(["plotly_json", "structure_json"]);
    expect(sourceResourceArtifacts(structure, [xrd, structure]).map((artifact) => artifact.type)).toEqual(["structure_json", "plotly_json"]);
  });

  it("provides a truthful structured source preview for raw volumetric fields", () => {
    const summary = projectVolumetricSourceSummary({
      source_format: "cube", source_name: "charge-density.cube", shape: [2, 3, 4], origin_cartesian: [0, 0, 0], step_matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], boundary_conditions: ["periodic", "periodic", "periodic"],
      channels: [{ name: "charge_density", quantity: "charge_density", canonical_unit: "e/angstrom^3", values: Array.from({ length: 24 }, (_, index) => index / 10) }],
    });
    const artifact = sourceResourceArtifact({ objectId: "volume-1", objectType: "VolumetricData", datasetId: "dataset-4", payload: { source_format: "cube", source_name: "charge-density.cube", shape: [2, 3, 4], boundary_conditions: ["periodic", "periodic", "periodic"], channels: [{ name: "charge_density", quantity: "charge_density", canonical_unit: "e/angstrom^3", values: Array(24).fill(0) }] } });

    expect(summary).toMatchObject({ rows: [{ field: "charge_density", quantity: "charge_density", unit: "e/angstrom^3", samples: 24, grid: "2 × 3 × 4" }], source: { sourceFormat: "cube", sourceName: "charge-density.cube" } });
    expect(artifact).toMatchObject({ type: "table_json", name: "体数据", content: { rows: [{ field: "charge_density", samples: 24 }] } });
  });

  it("projects bounded periodic source volumetric data into the canonical 3D viewer contract", () => {
    const resource = { objectId: "volume-3d", objectType: "VolumetricData", datasetId: "dataset-volume", payload: {
      source_format: "vasp_volumetric", source_name: "CHGCAR", source_sha256: "a".repeat(64), shape: [2, 2, 2], origin_cartesian: [0, 0, 0],
      step_matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], boundary_conditions: ["periodic", "periodic", "periodic"], endpoint_policy: "excluded", sample_location: "node",
      structure_sha256: "b".repeat(64), lattice_matrix: [[2, 0, 0], [0, 2, 0], [0, 0, 2]], channels: [{ name: "total", quantity: "electron_density", canonical_unit: "electron/angstrom^3", source_unit: "electron/angstrom^3", normalization_semantics: "source_native", integral_semantics: "electron_count", values: [0, 1, 2, 3, 4, 5, 6, 7] }], warnings: [],
    }};
    const artifacts = projectVolumetricSourceArtifacts(resource);
    expect(artifacts?.map((item) => item.type)).toEqual(["volumetric_dataset_json", "volumetric_manifest_json", "volumetric_grid_json"]);
    const dataset = artifacts?.find((item) => item.type === "volumetric_dataset_json")?.content;
    const manifest = artifacts?.find((item) => item.type === "volumetric_manifest_json")?.content;
    expect(validateVolumetricArtifacts(dataset, manifest)).toMatchObject({ ok: true });
  });

  it("projects non-periodic Gaussian cube data without inventing a structure binding", () => {
    const artifacts = projectVolumetricSourceArtifacts({ objectId: "cube", objectType: "VolumetricData", datasetId: "dataset-cube", payload: {
      source_format: "gaussian_cube", source_name: "density.cube", shape: [2, 2, 2], origin_cartesian: [0, 0, 0], step_matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
      boundary_conditions: ["non_periodic", "non_periodic", "non_periodic"], endpoint_policy: "not_applicable", sample_location: "node", channels: [{ name: "scalar", quantity: "generic_scalar", canonical_unit: "dimensionless", values: [1, 2, 3, 4, 5, 6, 7, 8] }],
    } });
    const dataset = artifacts?.find((item) => item.type === "volumetric_dataset_json")?.content as Record<string, unknown>;
    expect((dataset.grid as Record<string, unknown>).structure_binding).toBeNull();
    expect(validateVolumetricArtifacts(dataset, artifacts?.find((item) => item.type === "volumetric_manifest_json")?.content)).toMatchObject({ ok: true });
  });

  it("retains the source potential zero and uses affine voxel volume for profiles and shifted integrals", () => {
    const values = [0, 1, 2, 3, 4, 5, 6, 7];
    const artifacts = projectVolumetricSourceArtifacts({ objectId: "potential", objectType: "VolumetricData", datasetId: "dataset-potential", payload: {
      source_format: "vasp_volumetric", source_name: "LOCPOT", source_sha256: "a".repeat(64), shape: [2, 2, 2], origin_cartesian: [0, 0, 0],
      step_matrix: [[0.5, 0, 0], [0.2, 1, 0], [0, 0, -0.5]], boundary_conditions: ["periodic", "periodic", "periodic"], endpoint_policy: "excluded", sample_location: "node",
      structure_sha256: "b".repeat(64), lattice_matrix: [[1, 0, 0], [0.4, 2, 0], [0, 0, -1]],
      channels: [{ name: "local_potential", quantity: "local_potential", canonical_unit: "electronvolt", source_unit: "electronvolt", normalization_semantics: "source_native", integral_semantics: "cell_average", values }],
    } })!;
    const result = validateVolumetricArtifacts(artifacts[0].content, artifacts[1].content);
    expect(result.ok, JSON.stringify(result)).toBe(true);
    if (!result.ok) return;
    const field = result.bundle.fields[0].field;
    expect(buildElectrostaticPotentialProduct(result.bundle)).toMatchObject({ status: "ready", quantity: "local_potential", unit: "electronvolt", sourceReference: { kind: "source_defined", shiftApplied: false, shiftAmount: 0 } });
    expect(field).toMatchObject({ minimum: 0, maximum: 7, mean: 3.5, integral: 7 });
    expect(potentialGaugeView(field, result.bundle.grid, "cell_average_zero", null)).toMatchObject({ shift: -3.5, displayedMean: 0, displayedVolumeIntegral: 0 });
    const profile = planarProfiles(new Float64Array(values), result.bundle.grid, field, "source_native", 0)[0];
    expect(profile.points.map(point => point.sourceValue)).toEqual([1.5, 5.5]);
    expect(values).toEqual([0, 1, 2, 3, 4, 5, 6, 7]);
  });

  it("retains distinct source channels with identical numeric payloads", () => {
    const artifacts = projectVolumetricSourceArtifacts({ objectId: "equal-channels", objectType: "VolumetricData", datasetId: "dataset-cube", payload: {
      source_format: "gaussian_cube", shape: [2, 2, 2], origin_cartesian: [0, 0, 0], step_matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
      boundary_conditions: ["non_periodic", "non_periodic", "non_periodic"], sample_location: "node",
      channels: ["first", "second"].map(name => ({ name, quantity: "generic_scalar", canonical_unit: "dimensionless", values: Array(8).fill(0) })),
    } })!;
    const result = validateVolumetricArtifacts(artifacts[0].content, artifacts[1].content);
    expect(result.ok, JSON.stringify(result)).toBe(true);
    if (!result.ok) return;
    expect(result.bundle.fields.map(item => item.field.fieldName).sort()).toEqual(["first", "second"]);
    expect(new Set(result.bundle.fields.map(item => item.payload.payloadId)).size).toBe(1);
  });

  it("rejects non-finite or oversized source volumetric fields instead of projecting them", () => {
    const base = { objectId: "volume-invalid", objectType: "VolumetricData", datasetId: "dataset-volume", payload: { shape: [2, 2, 2], origin_cartesian: [0, 0, 0], step_matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], boundary_conditions: ["periodic", "periodic", "periodic"], channels: [{ values: [1, 2, 3, 4, 5, 6, 7, Number.NaN] }] } };
    expect(projectVolumetricSourceArtifacts(base)).toBeNull();
  });

  it("uses a validated in-memory binary payload for retained near-cap source grids", () => {
    const values = Array.from({ length: 125 * 72 * 60 }, (_, index) => Math.sin(index / 100));
    const artifacts = projectVolumetricSourceArtifacts({ objectId: "volume-near-cap", objectType: "VolumetricData", datasetId: "dataset-volume", payload: {
      source_format: "vasp_volumetric", source_sha256: "c".repeat(64), shape: [125, 72, 60], origin_cartesian: [0, 0, 0], step_matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], boundary_conditions: ["periodic", "periodic", "periodic"], endpoint_policy: "excluded", sample_location: "node", structure_sha256: "d".repeat(64), lattice_matrix: [[125, 0, 0], [0, 72, 0], [0, 0, 60]], channels: [{ name: "total", quantity: "electron_density", canonical_unit: "electron/angstrom^3", values }],
    } });
    expect(artifacts?.some((item) => item.type === "volumetric_binary" && item.sizeBytes === values.length * 8 && item.content instanceof ArrayBuffer)).toBe(true);
    const dataset = artifacts?.find((item) => item.type === "volumetric_dataset_json")?.content;
    const manifest = artifacts?.find((item) => item.type === "volumetric_manifest_json")?.content;
    expect(validateVolumetricArtifacts(dataset, manifest)).toMatchObject({ ok: true });
  });
});
