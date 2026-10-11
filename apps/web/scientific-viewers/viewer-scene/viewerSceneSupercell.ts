import { periodicSiteKey, translateCartesian } from "./viewerScenePeriodicGeometry";
import { savedSiteNeighbors } from "./viewerSiteNeighbors";
import type { ImageOffset, PeriodicSiteRef, RenderAtom, RenderBond, RenderVector3, ValidatedRenderScene } from "./viewerSceneRendererTypes";

export const PERIODIC_DERIVED_CAPS = Object.freeze({ maxAxisRepeat: 3, maxTotalCells: 27, maxDisplayedSites: 2048, maxDisplayedBonds: 8192, maxNeighborImages: 26, maxArtifactBytes: 16_384 });
export type SupercellRepeat = ImageOffset;
export type NeighborDisplay = number | Readonly<{ mode: "neighbors" | "image"; center: PeriodicSiteRef }>;
export type SupercellEstimate = Readonly<{ expansion: SupercellRepeat; totalCells: number; displayedAtoms: number; displayedBonds: number; mode: "interactive" | "degraded" | "refused"; warnings: readonly string[]; error: string | null }>;
export type SupercellDerivation = { readonly ok: true; readonly scene: ValidatedRenderScene; readonly offsets: readonly ImageOffset[] } | { readonly ok: false; readonly error: "PERIODIC_REPEAT_INVALID" | "PERIODIC_DERIVED_SITE_LIMIT_EXCEEDED" | "PERIODIC_DERIVED_BOND_LIMIT_EXCEEDED" | "PERIODIC_NEIGHBOR_IMAGE_LIMIT_EXCEEDED"; readonly requestedSites: number; readonly requestedBonds: number };

export function estimatePeriodicSupercell(scene: ValidatedRenderScene, repeat: unknown): SupercellEstimate {
  if (!validRepeat(repeat)) return Object.freeze({ expansion: Object.freeze([1,1,1]) as SupercellRepeat, totalCells: 0, displayedAtoms: 0, displayedBonds: 0, mode: "refused", warnings: Object.freeze([]), error: "VIEWER_SUPERCELL_INVALID_EXPANSION" });
  const totalCells = repeat[0] * repeat[1] * repeat[2];
  const offsets = supercellOffsets(repeat);
  const offsetKeys = new Set(offsets.map((offset) => offset.join(",")));
  const displayedAtoms = scene.atoms.length * totalCells;
  const displayedBonds = scene.bonds.reduce((count,bond)=>count+offsets.filter((cell)=>offsetKeys.has(addOffset(cell,bond.toRef.imageOffset).join(","))).length,0);
  const error = totalCells > PERIODIC_DERIVED_CAPS.maxTotalCells ? "VIEWER_SUPERCELL_TOTAL_CELL_LIMIT_EXCEEDED" : displayedAtoms > PERIODIC_DERIVED_CAPS.maxDisplayedSites ? "VIEWER_SUPERCELL_ATOM_BUDGET_EXCEEDED" : displayedBonds > PERIODIC_DERIVED_CAPS.maxDisplayedBonds ? "VIEWER_SUPERCELL_BOND_BUDGET_EXCEEDED" : null;
  const degraded = !error && (displayedAtoms > 1000 || displayedBonds > 4096);
  return Object.freeze({ expansion: Object.freeze([...repeat]) as SupercellRepeat, totalCells, displayedAtoms, displayedBonds, mode: error ? "refused" : degraded ? "degraded" : "interactive", warnings: Object.freeze(degraded ? ["VIEWER_SUPERCELL_DEGRADED_MODE"] : []), error });
}

export function derivePeriodicSupercell(scene: ValidatedRenderScene, repeat: SupercellRepeat, neighborSelection: NeighborDisplay | null = null): SupercellDerivation {
  if (!validRepeat(repeat)) return Object.freeze({ ok: false, error: "PERIODIC_REPEAT_INVALID", requestedSites: 0, requestedBonds: 0 });
  const offsets = supercellOffsets(repeat);
  const atomBySite = new Map(scene.atoms.map((atom) => [atom.siteIndex, atom] as const));
  const refs = new Map<string, { atom: RenderAtom; offset: ImageOffset }>();
  const addSite = (ref: PeriodicSiteRef) => {
    const atom = atomBySite.get(ref.siteIndex);
    if (atom) refs.set(periodicSiteKey(ref), { atom, offset: ref.imageOffset });
  };
  for (const offset of offsets) for (const atom of scene.atoms) addSite({ siteIndex: atom.siteIndex, imageOffset: offset });
  // A numeric selection retains the existing same-site periodic-copy view.
  // Image restoration adds exactly the selected image; a neighborhood adds
  // only its adjacent endpoints, with the same +/-3 policy as selection URLs.
  const center = typeof neighborSelection === "object" && neighborSelection ? neighborSelection.center : null;
  const neighbors = center && typeof neighborSelection === "object" && neighborSelection?.mode === "neighbors" ? savedSiteNeighbors(scene.bonds, center) : [];
  if (center && [center, ...neighbors.map(neighbor => neighbor.target)].some(ref => ref.imageOffset.some(value => !Number.isSafeInteger(value) || Math.abs(value) > 3))) {
    return Object.freeze({ ok: false, error: "PERIODIC_NEIGHBOR_IMAGE_LIMIT_EXCEEDED", requestedSites: refs.size, requestedBonds: 0 });
  }
  if (typeof neighborSelection === "number") {
    for (const offset of centeredNeighborOffsets()) addSite({ siteIndex: neighborSelection, imageOffset: offset });
  } else if (center) {
    addSite(center);
    for (const neighbor of neighbors) addSite(neighbor.target);
  }
  const requestedSites = refs.size;
  if (requestedSites > PERIODIC_DERIVED_CAPS.maxDisplayedSites) return Object.freeze({ ok: false, error: "PERIODIC_DERIVED_SITE_LIMIT_EXCEEDED", requestedSites, requestedBonds: 0 });

  const requests = new Map<string, { bond: RenderBond; fromRef: PeriodicSiteRef; toRef: PeriodicSiteRef }>();
  const addBond = (bond: RenderBond, fromRef: PeriodicSiteRef, toRef: PeriodicSiteRef) => {
    const fromKey = periodicSiteKey(fromRef), toKey = periodicSiteKey(toRef);
    if (!refs.has(fromKey) || !refs.has(toKey) || fromKey === toKey) return;
    const key = [fromKey, toKey].sort().join("|");
    if (!requests.has(key)) requests.set(key, { bond, fromRef, toRef });
  };
  for (const offset of offsets) for (const bond of scene.bonds) {
    addBond(bond,
      { siteIndex: bond.fromSiteIndex, imageOffset: addOffset(offset, bond.fromRef.imageOffset) },
      { siteIndex: bond.toSiteIndex, imageOffset: addOffset(offset, bond.toRef.imageOffset) });
  }
  // Connections are undirected. This also covers a selected endpoint that is
  // the canonical 'to' site and periodic self-neighbors in both directions.
  if (center) for (const { bond, target } of neighbors) addBond(bond, center, target);
  const requestedBonds = requests.size;
  if (requestedBonds > PERIODIC_DERIVED_CAPS.maxDisplayedBonds) return Object.freeze({ ok: false, error: "PERIODIC_DERIVED_BOND_LIMIT_EXCEEDED", requestedSites, requestedBonds });

  const atoms: RenderAtom[] = [];
  const positions = new Map<string, RenderVector3>();
  const orderedRefs = [...refs.values()].sort((left, right) => compareOffset(left.offset, right.offset) || left.atom.siteIndex - right.atom.siteIndex);
  for (const { atom, offset } of orderedRefs) {
    const ref = Object.freeze({ siteIndex: atom.siteIndex, imageOffset: Object.freeze([...offset]) as ImageOffset });
    const key = periodicSiteKey(ref);
    const position = translateCartesian(atom.canonicalPosition, ref.imageOffset, scene.lattice.matrix);
    positions.set(key, position);
    atoms.push(Object.freeze({ ...atom, id: `site-${key}`, ref, position }));
  }

  const bonds: RenderBond[] = [...requests.values()].flatMap(({ bond, fromRef, toRef }) => {
    const start = positions.get(periodicSiteKey(fromRef));
    const end = positions.get(periodicSiteKey(toRef));
    if (!start || !end || Math.hypot(start[0]-end[0],start[1]-end[1],start[2]-end[2]) <= 1e-9) return [];
    const id=`bond-${periodicSiteKey(fromRef)}-${periodicSiteKey(toRef)}`;
    const displacementCartesian:RenderVector3=Object.freeze([end[0]-start[0],end[1]-start[1],end[2]-start[2]]);
    return [Object.freeze({ ...bond, id, fromSiteIndex: fromRef.siteIndex, toSiteIndex: toRef.siteIndex, fromRef, toRef, start, end, displacementCartesian })];
  });
  const displayMatrix = Object.freeze(scene.lattice.matrix.map((row, axis) => Object.freeze(row.map((value) => value * repeat[axis])))) as ValidatedRenderScene["displayLattice"]["matrix"];
  return Object.freeze({
    ok: true,
    offsets: Object.freeze(offsets),
    scene: Object.freeze({ ...scene, atoms: Object.freeze(atoms), bonds: Object.freeze(bonds), displayLattice: Object.freeze({ matrix: displayMatrix }), supercellRepeat: Object.freeze([...repeat]) as ImageOffset }),
  });
}

export function supercellOffsets(repeat: SupercellRepeat): readonly ImageOffset[] {
  if (!validRepeat(repeat)) return Object.freeze([]);
  const offsets: ImageOffset[] = [];
  for (let x=0;x<repeat[0];x+=1) for(let y=0;y<repeat[1];y+=1) for(let z=0;z<repeat[2];z+=1) offsets.push(Object.freeze([x,y,z]));
  return Object.freeze(offsets);
}

export function centeredNeighborOffsets(): readonly ImageOffset[] {
  const offsets: ImageOffset[]=[];
  for(let x=-1;x<=1;x+=1) for(let y=-1;y<=1;y+=1) for(let z=-1;z<=1;z+=1) offsets.push(Object.freeze([x,y,z]));
  return Object.freeze(offsets);
}

export function validSupercellRepeat(value: unknown): value is SupercellRepeat { return Array.isArray(value) && value.length===3 && value.every((item)=>typeof item === "number"&&Number.isSafeInteger(item)&&item>=1&&item<=PERIODIC_DERIVED_CAPS.maxAxisRepeat); }
function validRepeat(value: unknown): value is SupercellRepeat { return validSupercellRepeat(value); }
function compareOffset(a: ImageOffset,b: ImageOffset) { return a[0]-b[0]||a[1]-b[1]||a[2]-b[2]; }
function addOffset(a:ImageOffset,b:ImageOffset):ImageOffset{return Object.freeze([a[0]+b[0],a[1]+b[1],a[2]+b[2]]);}
