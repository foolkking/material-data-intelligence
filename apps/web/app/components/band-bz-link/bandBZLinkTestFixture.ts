import stableBand from "../../../../../docs/phase10h/fixtures/phonon_contract/stable_band.json";
import manifest from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/manifest.json";
import reciprocal from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/reciprocal_lattice.json";
import zone from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/brillouin_zone.json";
import kpath from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/kpath.json";

import type { Artifact } from "../../lib/planner-api";

export function bandBZFixture() {
  const band = structuredClone(stableBand) as Record<string, any>;
  const selected = kpath.path_variants.find((item) => item.selected)!;
  const points = new Map(kpath.points.map((item) => [item.point_id, item]));
  const segments = selected.segment_ids.map((id) => kpath.segments.find((item) => item.segment_id === id)!);
  const qpoints: Record<string, unknown>[] = [];
  const bandSegments: Record<string, unknown>[] = [];
  let distance = 0;
  for (const [segmentIndex, segment] of segments.entries()) {
    const start = points.get(segment.start_point_id)!;
    const end = points.get(segment.end_point_id)!;
    const startIndex = qpoints.length;
    qpoints.push({ index:startIndex,coordinates:start.fractional_coordinates,label:start.display_label,source_label:start.label_key,segment_index:segmentIndex,distance });
    distance += segment.length;
    const endIndex = qpoints.length;
    qpoints.push({ index:endIndex,coordinates:end.fractional_coordinates,label:end.display_label,source_label:end.label_key,segment_index:segmentIndex,distance });
    bandSegments.push({ segment_index:segmentIndex,start_qpoint_index:startIndex,end_qpoint_index:endIndex,start_label:start.display_label,end_label:end.display_label,discontinuous_from_previous:segmentIndex>0&&segment.discontinuity_before });
  }
  band.structure_identity = reciprocal.real_lattice_binding.source_structure_sha256;
  band.real_space_lattice_angstrom = reciprocal.real_lattice_binding.primitive_real_lattice;
  band.qpoints = qpoints;
  band.segments = bandSegments;
  band.branches = band.branches.map((branch:Record<string,any>) => ({ ...branch, frequencies:qpoints.map((_,index) => branch.branch_index + index * .125 - (branch.branch_index === 0 && index === 1 ? .5 : 0)) }));
  band.degeneracy_groups = [];
  return { band, reciprocal:structuredClone(reciprocal), zone:structuredClone(zone), kpath:structuredClone(kpath), manifest:structuredClone(manifest) };
}

export function bandBZArtifacts(hash="a".repeat(64)): Artifact[] {
  const fixture=bandBZFixture();
  const artifact=(id:string,type:string,name:string,content:unknown,sha256?:string)=>({id,type,name,content,sha256,contentHash:sha256??"b".repeat(64)}) as Artifact;
  return [
    artifact("band","phonon_band_json","phonon_band.json",fixture.band,hash),
    artifact("reciprocal","reciprocal_lattice_json","reciprocal_lattice.json",fixture.reciprocal),
    artifact("zone","brillouin_zone_json","brillouin_zone.json",fixture.zone),
    artifact("kpath","kpath_json","kpath.json",fixture.kpath),
    artifact("manifest","brillouin_zone_manifest_json","brillouin_zone_manifest.json",fixture.manifest),
  ];
}
