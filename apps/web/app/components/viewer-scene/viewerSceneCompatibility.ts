export type ViewerSceneCompatibility = Readonly<{
  status:"deprecated_read_only"|"supported_legacy_same_cell"|"current"|"unsupported";
  previewMode:"json_only"|"json_or_renderer"|"unsupported";
  rendererSupported:boolean;
  periodicTopologySupported:boolean;
  migrationPolicy:"regenerate_from_source_only"|"not_required"|"unsupported";
  warnings:readonly string[];
}>;

export const VIEWER_SCENE_COMPATIBILITY = Object.freeze({
  "phase10d1.viewer_scene.v1": Object.freeze({status:"deprecated_read_only",previewMode:"json_only",rendererSupported:false,periodicTopologySupported:false,migrationPolicy:"regenerate_from_source_only",warnings:Object.freeze(["VIEWER_SCENE_LEGACY_PHASE10D_SCHEMA"])}),
  "phase10f8.viewer_scene.v1": Object.freeze({status:"supported_legacy_same_cell",previewMode:"json_or_renderer",rendererSupported:true,periodicTopologySupported:false,migrationPolicy:"regenerate_from_source_only",warnings:Object.freeze(["VIEWER_SCENE_LEGACY_SAME_CELL_TOPOLOGY"])}),
  "phase10f18.viewer_scene.v2": Object.freeze({status:"current",previewMode:"json_or_renderer",rendererSupported:true,periodicTopologySupported:true,migrationPolicy:"not_required",warnings:Object.freeze([])}),
} satisfies Record<string,ViewerSceneCompatibility>);

const UNSUPPORTED:ViewerSceneCompatibility=Object.freeze({status:"unsupported",previewMode:"unsupported",rendererSupported:false,periodicTopologySupported:false,migrationPolicy:"unsupported",warnings:Object.freeze(["VIEWER_SCENE_SCHEMA_UNSUPPORTED"])});

export function viewerSceneCompatibility(schema:unknown):ViewerSceneCompatibility {
  return typeof schema==="string"&&schema in VIEWER_SCENE_COMPATIBILITY ? VIEWER_SCENE_COMPATIBILITY[schema as keyof typeof VIEWER_SCENE_COMPATIBILITY] : UNSUPPORTED;
}

export const VIEWER_MANIFEST_COMPATIBILITY=Object.freeze({
  "phase10d1.viewer_assets_manifest.v1":Object.freeze({status:"deprecated_read_only",periodicTopologySupported:false,rendererIncluded:false,warnings:Object.freeze(["VIEWER_MANIFEST_LEGACY_PHASE10D_SCHEMA"]),pairedSceneSchema:"phase10d1.viewer_scene.v1"}),
  "phase10f9.viewer_scene_manifest.v1":Object.freeze({status:"supported_legacy",periodicTopologySupported:false,rendererIncluded:false,warnings:Object.freeze(["VIEWER_MANIFEST_LEGACY_V1_SCHEMA"]),pairedSceneSchema:"phase10f8.viewer_scene.v1"}),
  "phase10f19.viewer_assets_manifest.v2":Object.freeze({status:"current",periodicTopologySupported:true,rendererIncluded:false,warnings:Object.freeze([]),pairedSceneSchema:"phase10f18.viewer_scene.v2"}),
});

export function viewerManifestCompatibility(schema:unknown){
  return typeof schema==="string"&&schema in VIEWER_MANIFEST_COMPATIBILITY?VIEWER_MANIFEST_COMPATIBILITY[schema as keyof typeof VIEWER_MANIFEST_COMPATIBILITY]:Object.freeze({status:"unsupported",periodicTopologySupported:false,rendererIncluded:false,warnings:Object.freeze(["VIEWER_MANIFEST_SCHEMA_UNSUPPORTED"]),pairedSceneSchema:"unknown"});
}
