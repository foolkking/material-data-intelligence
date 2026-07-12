import { periodicSiteKey, translateCartesian } from "./viewerScenePeriodicGeometry";
import type { ImageOffset, PeriodicSiteRef, RenderAtom, RenderBond, RenderVector3, ValidatedRenderScene } from "./viewerSceneRendererTypes";

export const PERIODIC_DERIVED_CAPS = Object.freeze({ maxAxisRepeat: 3, maxDisplayedSites: 2048, maxDisplayedBonds: 8192, maxNeighborImages: 26 });
export type SupercellRepeat = ImageOffset;
export type SupercellDerivation = { readonly ok: true; readonly scene: ValidatedRenderScene; readonly offsets: readonly ImageOffset[] } | { readonly ok: false; readonly error: "PERIODIC_REPEAT_INVALID" | "PERIODIC_DERIVED_SITE_LIMIT_EXCEEDED" | "PERIODIC_DERIVED_BOND_LIMIT_EXCEEDED"; readonly requestedSites: number; readonly requestedBonds: number };

export function derivePeriodicSupercell(scene: ValidatedRenderScene, repeat: SupercellRepeat, neighborSiteIndex: number | null = null): SupercellDerivation {
  if (!validRepeat(repeat)) return Object.freeze({ ok: false, error: "PERIODIC_REPEAT_INVALID", requestedSites: 0, requestedBonds: 0 });
  const offsets = supercellOffsets(repeat);
  const neighborOffsets = neighborSiteIndex === null ? [] : centeredNeighborOffsets().filter((offset) => !offset.every((value) => value === 0));
  const requestedSites = scene.atoms.length * offsets.length + (scene.atoms.some((atom) => atom.siteIndex === neighborSiteIndex) ? neighborOffsets.length : 0);
  const offsetKeys = new Set(offsets.map((offset)=>offset.join(",")));
  const requestedBonds = scene.bonds.reduce((count,bond)=>count+offsets.filter((cell)=>offsetKeys.has(addOffset(cell,bond.toRef.imageOffset).join(","))).length,0);
  if (requestedSites > PERIODIC_DERIVED_CAPS.maxDisplayedSites) return Object.freeze({ ok: false, error: "PERIODIC_DERIVED_SITE_LIMIT_EXCEEDED", requestedSites, requestedBonds });
  if (requestedBonds > PERIODIC_DERIVED_CAPS.maxDisplayedBonds) return Object.freeze({ ok: false, error: "PERIODIC_DERIVED_BOND_LIMIT_EXCEEDED", requestedSites, requestedBonds });

  const atomBySite = new Map(scene.atoms.map((atom) => [atom.siteIndex, atom] as const));
  const refs = offsets.flatMap((offset) => scene.atoms.map((atom) => ({ atom, offset })))
    .concat(neighborOffsets.flatMap((offset) => {
      const atom = neighborSiteIndex === null ? undefined : atomBySite.get(neighborSiteIndex);
      return atom ? [{ atom, offset }] : [];
    }))
    .sort((left, right) => compareOffset(left.offset, right.offset) || left.atom.siteIndex - right.atom.siteIndex);
  const seen = new Set<string>();
  const atoms: RenderAtom[] = [];
  const positions = new Map<string, RenderVector3>();
  for (const { atom, offset } of refs) {
    const ref = Object.freeze({ siteIndex: atom.siteIndex, imageOffset: Object.freeze([...offset]) as ImageOffset });
    const key = periodicSiteKey(ref);
    if (seen.has(key)) continue;
    seen.add(key);
    const position = translateCartesian(atom.canonicalPosition, ref.imageOffset, scene.lattice.matrix);
    positions.set(key, position);
    atoms.push(Object.freeze({ ...atom, id: `site-${key}`, ref, position }));
  }

  const bondKeys=new Set<string>();
  const bonds: RenderBond[] = offsets.flatMap((offset) => scene.bonds.flatMap((bond) => {
    const fromRef = Object.freeze({ siteIndex: bond.fromSiteIndex, imageOffset: Object.freeze([...offset]) as ImageOffset });
    const toImage=addOffset(offset,bond.toRef.imageOffset);
    const toRef = Object.freeze({ siteIndex: bond.toSiteIndex, imageOffset: toImage });
    const start = positions.get(periodicSiteKey(fromRef));
    const end = positions.get(periodicSiteKey(toRef));
    if (!start || !end || Math.hypot(start[0]-end[0],start[1]-end[1],start[2]-end[2]) <= 1e-9) return [];
    const id=`bond-${periodicSiteKey(fromRef)}-${periodicSiteKey(toRef)}`;
    if(bondKeys.has(id))return[]; bondKeys.add(id);
    const displacementCartesian:RenderVector3=Object.freeze([end[0]-start[0],end[1]-start[1],end[2]-start[2]]);
    return [Object.freeze({ ...bond, id, fromRef, toRef, start, end, displacementCartesian })];
  }));
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

function validRepeat(value: ImageOffset) { return value.length===3 && value.every((item)=>Number.isSafeInteger(item)&&item>=1&&item<=PERIODIC_DERIVED_CAPS.maxAxisRepeat); }
function compareOffset(a: ImageOffset,b: ImageOffset) { return a[0]-b[0]||a[1]-b[1]||a[2]-b[2]; }
function addOffset(a:ImageOffset,b:ImageOffset):ImageOffset{return Object.freeze([a[0]+b[0],a[1]+b[1],a[2]+b[2]]);}
