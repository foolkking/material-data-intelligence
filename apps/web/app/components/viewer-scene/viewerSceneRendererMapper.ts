import type { ImageOffset, RenderAtom, RenderBond, RenderVector3, ValidatedRenderScene, ViewerSceneValidation } from "./viewerSceneRendererTypes";
import { translateCartesian } from "./viewerScenePeriodicGeometry";
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
    const fractionalPosition = finiteTriplet(site.frac) ? tuple(site.frac) : null;
    const occupancy = typeof site.occupancy === "number" && Number.isFinite(site.occupancy) && site.occupancy >= 0 && site.occupancy <= 1 ? site.occupancy : 1;
    const ref = Object.freeze({ siteIndex: index, imageOffset: Object.freeze([0, 0, 0]) as ImageOffset });
    return Object.freeze({ id: `site-${index}:0:0:0`, siteIndex: index, ref, species, element: species, label: String(site.label), occupancy, position, canonicalPosition: position, fractionalPosition, radius, color });
  });

  const vectors = payload.scene.lattice.vectors;
  if (!Array.isArray(vectors) || vectors.length !== 3 || !vectors.every(finiteTriplet)) return { ok: false, validation };
  const latticeMatrix: ValidatedRenderScene["lattice"]["matrix"] = Object.freeze([tuple(vectors[0]), tuple(vectors[1]), tuple(vectors[2])]);
  const periodic = payload.version === "viewer_scene.v2";
  const bonds: RenderBond[] = (Array.isArray(payload.scene.bonds) ? payload.scene.bonds : [])
    .filter(isRecord)
    .map((bond) => periodic && isRecord(bond.from) && isRecord(bond.to)
      ? ({ id:String(bond.id), from:Number(bond.from.site_index), to:Number(bond.to.site_index), fromOffset:offset(bond.from.image_offset), toOffset:offset(bond.to.image_offset), distance:Number(bond.distance_angstrom), displacement:tuple(bond.displacement_cartesian), source:String(bond.source) as RenderBond["source"], authoritative:bond.authoritative===true })
      : ({ id:`bond-${Number(bond.from)}-${Number(bond.to)}`, from:Number(bond.from), to:Number(bond.to), fromOffset:[0,0,0] as ImageOffset, toOffset:[0,0,0] as ImageOffset, distance:Number(bond.distance ?? 0), displacement:null, source:"legacy_same_cell" as const, authoritative:false }))
    .sort((left, right) => left.from - right.from || left.to - right.to || compareOffset(left.toOffset,right.toOffset))
    .flatMap((bond) => {
      const canonicalStart = positions.get(bond.from);
      const canonicalEnd = positions.get(bond.to);
      const start = canonicalStart ? translateCartesian(canonicalStart,bond.fromOffset,latticeMatrix) : null;
      const end = canonicalEnd ? translateCartesian(canonicalEnd,bond.toOffset,latticeMatrix) : null;
      if (!start || !end || vectorDistance(start, end) <= 1e-9) return [];
      const fromRef = Object.freeze({ siteIndex: bond.from, imageOffset: bond.fromOffset });
      const toRef = Object.freeze({ siteIndex: bond.to, imageOffset: bond.toOffset });
      const displacementCartesian = bond.displacement ?? Object.freeze([end[0]-start[0],end[1]-start[1],end[2]-start[2]]) as RenderVector3;
      return [Object.freeze({ id: bond.id, fromSiteIndex: bond.from, toSiteIndex: bond.to, fromRef, toRef, start, end, displacementCartesian, distanceAngstrom: bond.distance || vectorDistance(start,end), source:bond.source, authoritative:bond.authoritative })];
    });
  const source = isRecord(payload.source) ? payload.source : {};
  const metadata = isRecord(payload.metadata) ? payload.metadata : {};
  const warnings = [...validation.warnings];
  if (!periodic && bonds.length > 0) warnings.push("VIEWER_SCENE_LEGACY_SAME_CELL_TOPOLOGY");
  const scene: ValidatedRenderScene = Object.freeze({
    contractVersion: periodic ? "viewer_scene.v2" : "viewer_scene.v1",
    schemaVersion: periodic ? "phase10f18.viewer_scene.v2" : "phase10f8.viewer_scene.v1",
    atoms: Object.freeze(atoms),
    bonds: Object.freeze(bonds),
    lattice: Object.freeze({ matrix: latticeMatrix }),
    displayLattice: Object.freeze({ matrix: latticeMatrix }),
    supercellRepeat: Object.freeze([1,1,1]) as ImageOffset,
    source: Object.freeze({
      resourceId: safeText(source.resource_id),
      filename: safeText(source.filename),
      parser: safeText(source.parser),
    }),
    formula: safeText(metadata.formula) || "structure",
    warnings: Object.freeze(warnings),
  });
  return { ok: true, scene, validation };
}

function offset(value: unknown): ImageOffset { return finiteTriplet(value) ? Object.freeze(value.map(Number)) as ImageOffset : Object.freeze([0,0,0]); }
function compareOffset(a:ImageOffset,b:ImageOffset){return a[0]-b[0]||a[1]-b[1]||a[2]-b[2];}

function safeText(value: unknown) {
  return typeof value === "string" ? value.slice(0, 256) : "";
}

function tuple(value: unknown): RenderVector3 {
  if (!finiteTriplet(value)) return Object.freeze([0, 0, 0]);
  return Object.freeze([value[0], value[1], value[2]]);
}

function vectorDistance(left: RenderVector3, right: RenderVector3) {
  return Math.hypot(left[0] - right[0], left[1] - right[1], left[2] - right[2]);
}
