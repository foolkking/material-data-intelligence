import type { ImageOffset, RenderAtom, RenderBond, RenderVector3, ValidatedRenderScene, ViewerSceneValidation } from "./viewerSceneRendererTypes";
import { translateCartesian } from "./viewerScenePeriodicGeometry";
import { finiteTriplet, isRecord, validateViewerSceneForRenderer } from "./viewerSceneRendererValidation";
import { elementDisplayColor } from "./elementAppearance";

type MappingResult =
  | { readonly ok: true; readonly scene: ValidatedRenderScene; readonly validation: ViewerSceneValidation }
  | { readonly ok: false; readonly validation: ViewerSceneValidation };

const SAFE_HEX = /^#[0-9a-f]{6}$/i;

export function mapViewerSceneForRenderer(payload: unknown): MappingResult {
  const validation = validateViewerSceneForRenderer(payload);
  if (!validation.valid || !isRecord(payload) || !isRecord(payload.scene) || !Array.isArray(payload.scene.sites) || !isRecord(payload.scene.lattice)) {
    return { ok: false, validation };
  }

  const source = isRecord(payload.source) ? payload.source : {};
  const metadata = isRecord(payload.metadata) ? payload.metadata : {};
  const provenance = isRecord(payload.provenance) ? payload.provenance : {};
  const connectivity = isRecord(metadata.connectivity) ? metadata.connectivity : {};
  const sceneStyle = isRecord(payload.scene.style) ? payload.scene.style : {};
  const idealModel = payload.version === "viewer_scene.v2" && source.tool_id === "generation.ideal_crystal"
    && source.resource_type === "ideal_model" && source.resource_id === `parameters:${provenance.parameter_hash}`
    && provenance.tool_id === source.tool_id && provenance.input_origin === "IDEAL_MODEL" && provenance.sample_analysis === false
    && typeof provenance.parameter_hash === "string" && /^[a-f0-9]{64}$/.test(provenance.parameter_hash)
    && metadata.model_kind === "ideal_crystal" && metadata.input_origin === "IDEAL_MODEL"
    && connectivity.kind === "distance_neighbors" && connectivity.method === "ideal_first_shell" && connectivity.chemical_bond_claim === false
    && Array.isArray(payload.scene.bonds) && payload.scene.bonds.every(bond => isRecord(bond) && bond.authoritative === false && bond.source === "distance_cutoff");
  const orderedSites = payload.scene.sites.filter(isRecord).slice().sort((left, right) => Number(left.index) - Number(right.index));
  const positions = new Map<number, RenderVector3>();
  const atoms: RenderAtom[] = orderedSites.map((site) => {
    const index = Number(site.index);
    const position = tuple(site.xyz);
    positions.set(index, position);
    const species = String(site.element);
    const style = isRecord(site.style) ? site.style : {};
    const paletteColor = elementDisplayColor(species);
    // This generator's default preset contains legacy fallback colors, not user styling.
    // Apply the shared element convention without rewriting its saved scene or geometry.
    const color = idealModel && sceneStyle.style_preset === "default" ? paletteColor
      : typeof style.color === "string" && SAFE_HEX.test(style.color) ? style.color.toLowerCase() : paletteColor;
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
  const previewWarning = metadata.display_only === true && Array.isArray(payload.warnings)
    ? payload.warnings.find(warning => isRecord(warning) && ["VIEWER_PREVIEW_CONNECTIONS_UNAVAILABLE", "VIEWER_SCENE_RADII_UNAVAILABLE"].includes(String(warning.code)))
    : undefined;
  const warnings = [...validation.warnings];
  if (Array.isArray(payload.warnings)) {
    for (const warning of payload.warnings) {
      const message = typeof warning === "string"
        ? warning.slice(0, 512)
        : isRecord(warning) && typeof warning.message === "string"
          ? warning.message.slice(0, 512)
          : "";
      if (message && !warnings.includes(message)) warnings.push(message);
    }
  }
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
    ...(metadata.display_only === true ? { sourcePreview: true } : {}),
    ...(isRecord(previewWarning) && typeof previewWarning.message === "string" ? { sourcePreviewWarning: previewWarning.message.slice(0, 512) } : {}),
    ...(connectivity.method === "covalent_radii" && connectivity.authoritative === false
        && typeof connectivity.radius_scale === "number" && Number.isFinite(connectivity.radius_scale)
        && connectivity.radius_scale > 0 && connectivity.radius_scale <= 2
      ? { connectivity: Object.freeze({ method: "covalent_radii" as const, radiusScale: connectivity.radius_scale, radiusReference: safeText(connectivity.radius_reference) }) }
      : idealModel ? { connectivity: Object.freeze({ method: "ideal_first_shell" as const }) } : {}),
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
