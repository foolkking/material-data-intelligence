import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {describe, expect, it} from "vitest";
import {fractionalToCartesian, validateTrajectoryReference} from "./trajectoryContract";

const fixtures = resolve(process.cwd(), "../../docs/phase10g/fixtures/trajectory_v1");
const load = (name: string) => JSON.parse(readFileSync(resolve(fixtures, name), "utf8"));

describe("Phase 10G independent trajectory reference", () => {
  it.each(["fixed_lattice_md.json", "variable_lattice_relaxation.json", "unwrapped_diffusion.json", "nonperiodic_sequence.json"])("accepts %s", (name) => {
    expect(validateTrajectoryReference(load(name))).toMatchObject({valid: true});
  });

  it.each([
    ["invalid_atom_count.json", "TRAJECTORY_ATOM_COUNT_MISMATCH"],
    ["invalid_species_reorder.json", "TRAJECTORY_SPECIES_MISMATCH"],
    ["invalid_lattice.json", "TRAJECTORY_LATTICE_SINGULAR"],
    ["invalid_time.json", "TRAJECTORY_TIME_NONMONOTONIC"],
  ])("rejects %s", (name, error) => {
    expect(validateTrajectoryReference(load(name)).errors).toContain(error);
  });

  it("uses row lattice vectors without wrapping unwrapped coordinates", () => {
    expect(fractionalToCartesian([1.1, 0.25, -0.5], [[2, 0, 0], [1, 3, 0], [0, 0, 4]])).toEqual([2.45, 0.75, -2]);
    expect(load("unwrapped_diffusion.json").frames[2].positions[0][0]).toBeGreaterThan(1);
  });

  it("matches the committed frontend/backend comparison evidence", () => {
    const comparison = JSON.parse(readFileSync(resolve(process.cwd(), "../../docs/phase10g/evidence/phase10g_trajectory_contract/frontend_backend_validation_comparison.json"), "utf8"));
    for (const [name, expected] of Object.entries(comparison.fixtures) as Array<[string, {python_valid: boolean; typescript_expected_valid: boolean}]>) {
      const actual = validateTrajectoryReference(load(name)).valid;
      expect(actual).toBe(expected.typescript_expected_valid);
      expect(actual).toBe(expected.python_valid);
    }
    expect(comparison.result).toBe("MATCH");
  });
});
