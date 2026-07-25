import type { VolumeMatrix3, VolumeVector3, VolumetricStructureOverlay } from "./volumetricViewerTypes";
import { VOLUMETRIC_BROWSER_CAPS } from "./volumetricViewerTypes";

export const VOLUMETRIC_OVERLAY_MAXIMUM_ATOMS = 4096;
export const VOLUMETRIC_OVERLAY_MAXIMUM_BONDS = 8192;

export type VolumetricOverlaySupercell = Readonly<{
  overlay: VolumetricStructureOverlay | null;
  repeat: 1 | 2;
  replicas: number;
  atomCount: number;
  bondCount: number;
  status: "primary_cell" | "replicated" | "non_periodic" | "cap_exceeded";
}>;

export function deriveVolumetricOverlaySupercell(
  source: VolumetricStructureOverlay | null,
  requestedRepeat: number,
): VolumetricOverlaySupercell {
  const repeat: 1 | 2 = requestedRepeat === 2 ? 2 : 1;
  if (!source) return Object.freeze({ overlay: null, repeat: 1, replicas: 1, atomCount: 0, bondCount: 0, status: "primary_cell" });
  if (source.kind !== "periodic_viewer_scene" || !source.lattice) {
    return Object.freeze({ overlay: source, repeat: 1, replicas: 1, atomCount: source.atoms.length, bondCount: source.bonds.length, status: "non_periodic" });
  }
  if (repeat === 1) return Object.freeze({ overlay: source, repeat, replicas: 1, atomCount: source.atoms.length, bondCount: source.bonds.length, status: "primary_cell" });
  const replicas = repeat ** 3;
  const atomCount = source.atoms.length * replicas;
  const bondCount = source.bonds.length * replicas;
  if (replicas > VOLUMETRIC_BROWSER_CAPS.maximumSupercellReplicas || atomCount > VOLUMETRIC_OVERLAY_MAXIMUM_ATOMS || bondCount > VOLUMETRIC_OVERLAY_MAXIMUM_BONDS) {
    return Object.freeze({ overlay: source, repeat: 1, replicas: 1, atomCount: source.atoms.length, bondCount: source.bonds.length, status: "cap_exceeded" });
  }
  const offsets = Array.from({ length: repeat }, (_, i) => i).flatMap((i) =>
    Array.from({ length: repeat }, (_, j) => j).flatMap((j) =>
      Array.from({ length: repeat }, (_, k) => Object.freeze([i, j, k] as const)),
    ),
  );
  const translation = (offset: readonly [number, number, number]): VolumeVector3 => Object.freeze([
    offset[0] * source.lattice![0][0] + offset[1] * source.lattice![1][0] + offset[2] * source.lattice![2][0],
    offset[0] * source.lattice![0][1] + offset[1] * source.lattice![1][1] + offset[2] * source.lattice![2][1],
    offset[0] * source.lattice![0][2] + offset[1] * source.lattice![1][2] + offset[2] * source.lattice![2][2],
  ]);
  const shifted = (point: VolumeVector3, offset: readonly [number, number, number]): VolumeVector3 => {
    const delta = translation(offset);
    return Object.freeze([point[0] + delta[0], point[1] + delta[1], point[2] + delta[2]]);
  };
  const atoms = offsets.flatMap((offset) => source.atoms.map((atom) => Object.freeze({ ...atom, position: shifted(atom.position, offset) })));
  const bonds = offsets.flatMap((offset) => source.bonds.map((bond) => Object.freeze({ ...bond, id: `${bond.id}@${offset.join(":")}`, start: shifted(bond.start, offset), end: shifted(bond.end, offset) })));
  const lattice = Object.freeze(source.lattice.map((row) => Object.freeze(row.map((value) => value * repeat) as [number, number, number])) as unknown as VolumeMatrix3);
  const overlay = Object.freeze({ ...source, atoms: Object.freeze(atoms), bonds: Object.freeze(bonds), lattice });
  return Object.freeze({ overlay, repeat, replicas, atomCount, bondCount, status: "replicated" });
}
