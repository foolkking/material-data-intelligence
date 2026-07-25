import { describe, expect, it } from "vitest";

import { deriveVolumetricOverlaySupercell } from "./volumetricOverlaySupercell";
import type { VolumetricStructureOverlay } from "./volumetricViewerTypes";

const periodic: VolumetricStructureOverlay = Object.freeze({
  kind: "periodic_viewer_scene",
  atoms: Object.freeze([{ siteIndex: 3, species: "Si", position: Object.freeze([0, 0, 0] as const), radius: 0.5, color: "#ffffff" }]),
  bonds: Object.freeze([{ id: "bond", start: Object.freeze([0, 0, 0] as const), end: Object.freeze([1, 0, 0] as const) }]),
  lattice: Object.freeze([Object.freeze([2, 0, 0] as const), Object.freeze([0, 3, 0] as const), Object.freeze([0, 0, 4] as const)] as const),
  unavailableReason: null,
});

describe("volumetric structure overlay supercell", () => {
  it("keeps the source overlay immutable at one cell", () => {
    const result = deriveVolumetricOverlaySupercell(periodic, 1);
    expect(result).toMatchObject({ status: "primary_cell", replicas: 1, atomCount: 1, bondCount: 1 });
    expect(result.overlay).toBe(periodic);
  });

  it("derives a deterministic bounded 2x2x2 display overlay", () => {
    const result = deriveVolumetricOverlaySupercell(periodic, 2);
    expect(result).toMatchObject({ status: "replicated", replicas: 8, atomCount: 8, bondCount: 8 });
    expect(result.overlay?.atoms.at(-1)?.position).toEqual([2, 3, 4]);
    expect(result.overlay?.bonds.at(-1)).toMatchObject({ id: "bond@1:1:1", start: [2, 3, 4], end: [3, 3, 4] });
    expect(result.overlay?.lattice).toEqual([[4, 0, 0], [0, 6, 0], [0, 0, 8]]);
    expect(periodic.atoms).toHaveLength(1);
  });

  it("does not replicate non-periodic atom context", () => {
    const source = Object.freeze({ ...periodic, kind: "non_periodic_atom_context", lattice: null, bonds: Object.freeze([]) }) satisfies VolumetricStructureOverlay;
    expect(deriveVolumetricOverlaySupercell(source, 2)).toMatchObject({ status: "non_periodic", repeat: 1, replicas: 1 });
  });

  it("rejects a derived atom allocation beyond the product cap", () => {
    const atoms = Object.freeze(Array.from({ length: 513 }, (_, siteIndex) => Object.freeze({ ...periodic.atoms[0], siteIndex })));
    const source = Object.freeze({ ...periodic, atoms }) satisfies VolumetricStructureOverlay;
    expect(deriveVolumetricOverlaySupercell(source, 2)).toMatchObject({ status: "cap_exceeded", repeat: 1, atomCount: 513 });
  });
});
