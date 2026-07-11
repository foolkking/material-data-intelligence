import type { RenderAtom, RenderBond, RenderVector3, ValidatedRenderScene, ViewerSceneValidation } from "./viewerSceneRendererTypes";
import { finiteTriplet, isRecord, validateViewerSceneForRenderer } from "./viewerSceneRendererValidation";

type MappingResult =
  | { readonly ok: true; readonly scene: ValidatedRenderScene; readonly validation: ViewerSceneValidation }
  | { readonly ok: false; readonly validation: ViewerSceneValidation };

const SPECIES_PALETTE = ["#2f7f8f", "#d56a45", "#7b61a8", "#4f8d58", "#c08b28", "#476aa3", "#a74f6f", "#64748b"] as const;
const SAFE_HEX = /^#[0-9a-f]{6}$/i;

export function mapViewerSceneForRenderer(payload: unknown): MappingResult {
  const validation = validateViewerSceneForRenderer(payload);
  if (!validation.valid || !isRecord(payload) || !isRecord(payload.scene) || !Array.isArray(payload.scene.sites) || !isRecord(payload.scene.lattice)) {
    return { ok: false, validation };
  }

  const orderedSites = payload.scene.sites.filter(isRecord).slice().sort((left, right) => Number(left.index) - Number(right.index));
  const speciesOrder = [...new Set(orderedSites.map((site) => String(site.element)))].sort();
  const positions = new Map<number, RenderVector3>();
  const atoms: RenderAtom[] = orderedSites.map((site) => {
    const index = Number(site.index);
    const position = tuple(site.xyz);
    positions.set(index, position);
    const species = String(site.element);
    const style = isRecord(site.style) ? site.style : {};
    const paletteColor = SPECIES_PALETTE[speciesOrder.indexOf(species) % SPECIES_PALETTE.length];
    const color = typeof style.color === "string" && SAFE_HEX.test(style.color) ? style.color.toLowerCase() : paletteColor;
    const radius = typeof style.radius === "number" && Number.isFinite(style.radius) && style.radius > 0 && style.radius <= 3 ? style.radius : 0.72;
    return Object.freeze({ id: `site-${index}`, siteIndex: index, species, label: String(site.label), position, radius, color });
  });

  const bonds: RenderBond[] = (Array.isArray(payload.scene.bonds) ? payload.scene.bonds : [])
    .filter(isRecord)
    .map((bond) => ({ from: Number(bond.from), to: Number(bond.to) }))
    .sort((left, right) => left.from - right.from || left.to - right.to)
    .flatMap((bond) => {
      const start = positions.get(bond.from);
      const end = positions.get(bond.to);
      if (!start || !end || vectorDistance(start, end) <= 1e-9) return [];
      return [Object.freeze({ id: `bond-${bond.from}-${bond.to}`, fromSiteIndex: bond.from, toSiteIndex: bond.to, start, end })];
    });

  const vectors = payload.scene.lattice.vectors;
  if (!Array.isArray(vectors) || vectors.length !== 3 || !vectors.every(finiteTriplet)) return { ok: false, validation };
  const latticeMatrix: ValidatedRenderScene["lattice"]["matrix"] = Object.freeze([tuple(vectors[0]), tuple(vectors[1]), tuple(vectors[2])]);
  const scene: ValidatedRenderScene = Object.freeze({
    contractVersion: "viewer_scene.v1",
    schemaVersion: "phase10f8.viewer_scene.v1",
    atoms: Object.freeze(atoms),
    bonds: Object.freeze(bonds),
    lattice: Object.freeze({ matrix: latticeMatrix }),
    warnings: Object.freeze([...validation.warnings]),
  });
  return { ok: true, scene, validation };
}

function tuple(value: unknown): RenderVector3 {
  if (!finiteTriplet(value)) return Object.freeze([0, 0, 0]);
  return Object.freeze([value[0], value[1], value[2]]);
}

function vectorDistance(left: RenderVector3, right: RenderVector3) {
  return Math.hypot(left[0] - right[0], left[1] - right[1], left[2] - right[2]);
}
