import multiSpeciesScene from "../../../../../tests/fixtures/viewer_scene_v1/valid_multi_species_crystal.viewer_scene.v1.json";

export function periodicBoundaryScene() {
  const payload = structuredClone(multiSpeciesScene) as Record<string, any>;
  payload.version = "viewer_scene.v2";
  payload.schema_version = "phase10f18.viewer_scene.v2";
  payload.capabilities = {periodic_structure:true,periodic_bonds:true,cross_boundary_bonds:true,neighbor_graph:true,trajectory:false,phonon:false,volumetric:false};
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

/** Saved-generator presentation fixture; the periodic geometry stays explicit. */
export function idealCrystalScene() {
  const payload = periodicBoundaryScene();
  const inputHash = "a".repeat(64);
  payload.source = { ...payload.source, tool_id: "generation.ideal_crystal", resource_type: "ideal_model", resource_id: `parameters:${inputHash}` };
  payload.provenance = { ...payload.provenance, tool_id: "generation.ideal_crystal", input_origin: "IDEAL_MODEL", sample_analysis: false, parameter_hash: inputHash };
  payload.metadata = { ...payload.metadata, formula: "Cu", species: ["Cu"], species_count: 1, model_kind: "ideal_crystal", input_origin: "IDEAL_MODEL",
    connectivity: { kind: "distance_neighbors", method: "ideal_first_shell", chemical_bond_claim: false } };
  payload.scene.style = { ...payload.scene.style, style_preset: "default" };
  payload.scene.sites.forEach((site: Record<string, unknown>, index: number) => { site.element = "Cu"; site.label = `Cu${index + 1}`; site.style = { color: "#888888", radius: 1 }; });
  return payload;
}
