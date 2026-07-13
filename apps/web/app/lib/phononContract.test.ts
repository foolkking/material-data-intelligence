import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  convertFrequency,
  PHONON_BAND_SCHEMA_VERSION,
  PHONON_DOS_SCHEMA_VERSION,
  reciprocalFractionalToCartesian,
  reciprocalLatticePhysics2Pi,
  validatePhononBandReference,
  validatePhononDosReference,
} from "./phononContract";

const security = {contains_javascript: false, contains_html: false, external_urls_allowed: false, executable_content_allowed: false, external_assets: []};
const source = {producer: "fixture", producer_version: "1.0", calculation_method: "finite_displacement", force_constants_source: "force_constants", supercell_matrix: [[2,0,0],[0,2,0],[0,0,2]], primitive_matrix: [[1,0,0],[0,1,0],[0,0,1]], nac: {enabled: false, gamma_direction: null, direction_policy: null}, input_sha256: "b".repeat(64), adapter_version: "phase10h-fixture-v1"};

function band() {
  const lattice = [[5,0,0],[0,5,0],[0,0,5]];
  return {
    schema_version: PHONON_BAND_SCHEMA_VERSION, structure_identity: "a".repeat(64), atom_count: 1,
    species: ["Si"], atom_ordering: "canonical_structure_order", real_space_lattice_angstrom: lattice,
    reciprocal_convention: "physics_2pi", qpoint_coordinate_system: "reciprocal_fractional",
    path_distance_unit: "radian_per_angstrom", frequency_unit: "terahertz",
    imaginary_frequency_encoding: "negative_real", frequency_zero_tolerance: 1e-6, branch_scope: "full",
    qpoints: [
      {index: 0, coordinates: [0,0,0], label: "Γ", source_label: "GAMMA", segment_index: 0, distance: 0},
      {index: 1, coordinates: [0.5,0,0], label: "X", source_label: "X", segment_index: 0, distance: Math.PI / 5},
    ],
    segments: [{segment_index: 0, start_qpoint_index: 0, end_qpoint_index: 1, start_label: "Γ", end_label: "X", discontinuous_from_previous: false}],
    branches: [
      {branch_index: 0, frequencies: [0,1]}, {branch_index: 1, frequencies: [0,1.1]}, {branch_index: 2, frequencies: [0,1.2]},
    ],
    degeneracy_groups: [{qpoint_index: 0, branch_indices: [0,1,2], source: "producer"}],
    acoustic_sum_rule: {applied: false, method: null}, source, warnings: [], security,
  };
}

function dos() {
  return {
    schema_version: PHONON_DOS_SCHEMA_VERSION, structure_identity: "a".repeat(64), atom_count: 1,
    species: ["Si"], atom_ordering: "canonical_structure_order", frequency_unit: "terahertz",
    imaginary_frequency_encoding: "negative_real", frequency_zero_tolerance: 1e-6,
    density_unit: "modes_per_terahertz", normalization: "total_modes", frequency_grid_semantics: "sample_grid_points",
    frequencies: [-1,0,1], total_dos: [1.5,1.5,1.5], projected_dos: [],
    broadening: {method: "none", width: null, unit: null, source: "fixture"},
    integration: {method: "trapezoidal", expected_mode_count: 3, observed_integral: 3, relative_tolerance: 0.01, status: "within_tolerance"},
    source, warnings: [], security,
  };
}

describe("Phase 10H phonon reference contract", () => {
  it("accepts canonical band and DOS shapes", () => {
    expect(validatePhononBandReference(band())).toMatchObject({valid: true, atomCount: 1, qpointCount: 2, branchCount: 3});
    expect(validatePhononDosReference(dos())).toMatchObject({valid: true, atomCount: 1, dosPointCount: 3});
  });

  it("rejects branch, DOS grid, and inertness violations", () => {
    const invalidBand = band();
    invalidBand.branches.pop();
    expect(validatePhononBandReference(invalidBand).errors).toContain("PHONON_BRANCH_COUNT_MISMATCH");
    const invalidDos = dos();
    invalidDos.frequencies = [0,0,1];
    expect(validatePhononDosReference(invalidDos).errors).toContain("PHONON_DOS_GRID_INVALID");
    expect(validatePhononBandReference({...band(), callback: "run"}).errors).toContain("PHONON_EXTERNAL_REFERENCE_FORBIDDEN");
  });

  it("uses row-vector 2pi reciprocal convention", () => {
    const reciprocal = reciprocalLatticePhysics2Pi([[4,0,0],[1,3,0],[0.2,0.4,5]]);
    const cartesian = reciprocalFractionalToCartesian([0.25,0.5,0.75], [[4,0,0],[1,3,0],[0.2,0.4,5]]);
    expect(reciprocal.flat().every(Number.isFinite)).toBe(true);
    expect(cartesian.every(Number.isFinite)).toBe(true);
    expect(reciprocalLatticePhysics2Pi([[5,0,0],[0,5,0],[0,0,5]])[0][0]).toBeCloseTo(2 * Math.PI / 5, 13);
  });

  it("uses exact SI frequency conversions", () => {
    expect(convertFrequency(1, "terahertz", "inverse_centimeter")).toBeCloseTo(33.3564095198152, 12);
    expect(convertFrequency(1, "terahertz", "millielectronvolt")).toBeCloseTo(4.135667696923859, 12);
    expect(() => convertFrequency(1, "radian_per_second", "terahertz")).toThrow("PHONON_FREQUENCY_UNIT_UNSUPPORTED");
  });

  it("accepts and rejects the committed cross-language fixtures", () => {
    const root = resolve(process.cwd(), "../..");
    const load = (name: string) => JSON.parse(readFileSync(resolve(root, "docs/phase10h/fixtures/phonon_contract", name), "utf8"));
    expect(validatePhononBandReference(load("stable_band.json")).valid).toBe(true);
    expect(validatePhononBandReference(load("imaginary_band.json")).valid).toBe(true);
    expect(validatePhononBandReference(load("discontinuous_band.json")).valid).toBe(true);
    expect(validatePhononDosReference(load("projected_dos.json")).valid).toBe(true);
    expect(validatePhononBandReference(load("invalid_branch_count.json")).valid).toBe(false);
    expect(validatePhononDosReference(load("invalid_dos_grid.json")).valid).toBe(false);
    const comparison = load("../../evidence/phase10h_phonon_contract/frontend_backend_validation_comparison.json");
    expect(comparison.result).toBe("PASS");
  });
});
