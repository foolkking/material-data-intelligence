"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../lib/planner-api";
import { BrillouinZoneSurface, type BrillouinZoneSurfaceProps } from "./BrillouinZoneSurface";

type PreviewTab = "renderer" | "data" | "manifest";

export type BrillouinZonePreviewPanelProps = Readonly<{
  artifacts: readonly Artifact[];
  capabilityOverride?: boolean;
  engineFactory?: BrillouinZoneSurfaceProps["engineFactory"];
}>;

export function BrillouinZonePreviewPanel({artifacts,capabilityOverride,engineFactory}:BrillouinZonePreviewPanelProps) {
  const reciprocalArtifact=findArtifact(artifacts,"reciprocal_lattice_json","reciprocal_lattice.json");
  const zoneArtifact=findArtifact(artifacts,"brillouin_zone_json","brillouin_zone.json");
  const kpathArtifact=findArtifact(artifacts,"kpath_json","kpath.json");
  const manifestArtifact=findArtifact(artifacts,"brillouin_zone_manifest_json","brillouin_zone_manifest.json");
  const summaryArtifact=findArtifact(artifacts,"summary_md","summary.md");
  const recipeArtifact=findArtifact(artifacts,"recipe_json","recipe.json");
  const [active,setActive]=useState<PreviewTab>("renderer");
  const bundle=useMemo(()=>({reciprocal:payload(reciprocalArtifact),zone:payload(zoneArtifact),kpath:kpathArtifact?payload(kpathArtifact):undefined,manifest:payload(manifestArtifact)}),[reciprocalArtifact,zoneArtifact,kpathArtifact,manifestArtifact]);
  if(!reciprocalArtifact&&!zoneArtifact&&!manifestArtifact)return null;
  const entries=[
    ["Reciprocal lattice",payload(reciprocalArtifact)],
    ["Brillouin zone",payload(zoneArtifact)],
    ["K-path",kpathArtifact?payload(kpathArtifact):null],
  ] as const;
  return <section className="panel viewer-static-preview brillouin-zone-preview" data-testid="brillouin-zone-preview-panel">
    <div className="brillouin-zone-product-heading"><div><h2>Brillouin Zone Viewer</h2><p>Application-owned Three.js consumer of validated inert Phase 10I artifacts.</p></div><span>Standalone reciprocal-space product</span></div>
    <div className="viewer-preview-tabs" role="tablist" aria-label="Brillouin zone preview modes">
      <button type="button" role="tab" aria-selected={active==="renderer"} className={active==="renderer"?"active":"secondary"} onClick={()=>setActive("renderer")}>3D Renderer</button>
      <button type="button" role="tab" aria-selected={active==="data"} className={active==="data"?"active":"secondary"} onClick={()=>setActive("data")}>Scientific data</button>
      <button type="button" role="tab" aria-selected={active==="manifest"} className={active==="manifest"?"active":"secondary"} onClick={()=>setActive("manifest")}>Manifest</button>
    </div>
    <div role="tabpanel" className="viewer-preview-tab-panel">
      {active==="renderer"?<BrillouinZoneSurface bundle={bundle} capabilityOverride={capabilityOverride} engineFactory={engineFactory} summary={textPayload(summaryArtifact)} recipe={payload(recipeArtifact)}/>:null}
      {active==="data"?<div className="brillouin-zone-json-grid">{entries.map(([label,value])=><details key={label} open={label==="Brillouin zone"}><summary>{label}</summary>{value?<pre className="json-preview">{JSON.stringify(value,null,2)}</pre>:<p className="empty-state">Not emitted by this validated package.</p>}</details>)}</div>:null}
      {active==="manifest"?<pre className="json-preview" data-testid="brillouin-zone-manifest-json">{JSON.stringify(payload(manifestArtifact),null,2)}</pre>:null}
    </div>
  </section>;
}

function findArtifact(artifacts:readonly Artifact[],type:string,name:string){return artifacts.find((item)=>item.type===type||item.name===name);}
function payload(artifact:Artifact|undefined):unknown { if(!artifact)return null;const content=artifact.content??artifact.metadata;if(typeof content==="string")try{return JSON.parse(content);}catch{return content;}return content??artifact; }
function textPayload(artifact:Artifact|undefined):string|undefined { const value=payload(artifact);return typeof value==="string"?value:undefined; }
