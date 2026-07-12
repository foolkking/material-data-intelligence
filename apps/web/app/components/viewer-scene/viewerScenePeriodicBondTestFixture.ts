import multiSpeciesScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_multi_species_crystal.viewer_scene.v1.json";

export function periodicBoundaryScene() {
  const payload = structuredClone(multiSpeciesScene) as Record<string, any>;
  payload.version = "viewer_scene.v2";
  payload.schema_version = "phase10f18.viewer_scene.v2";
  payload.scene.lattice.vectors = [[10,0,0],[0,10,0],[0,0,10]];
  payload.scene.sites[0].frac = [0.98,0,0]; payload.scene.sites[0].xyz = [9.8,0,0];
  payload.scene.sites[1].frac = [0.02,0,0]; payload.scene.sites[1].xyz = [0.2,0,0];
  payload.scene.bonds = [{
    id:"bond:0:0,0,0->1:1,0,0",
    from:{site_index:0,image_offset:[0,0,0]},
    to:{site_index:1,image_offset:[1,0,0]},
    displacement_cartesian:[0.4,0,0],
    distance_angstrom:0.4,
    source:"distance_cutoff",
    authoritative:false,
  }];
  return payload;
}
