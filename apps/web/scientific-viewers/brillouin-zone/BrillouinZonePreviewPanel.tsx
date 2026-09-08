"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../app/lib/planner-api";
import { BrillouinZoneSurface, type BrillouinZoneSurfaceProps } from "./BrillouinZoneSurface";

type PreviewTab = "renderer" | "data" | "manifest";

export type BrillouinZonePreviewPanelProps = Readonly<{
  artifacts: readonly Artifact[];
  capabilityOverride?: boolean;
  engineFactory?: BrillouinZoneSurfaceProps["engineFactory"];
}>;

export function BrillouinZonePreviewPanel({artifacts,capabilityOverride,engineFactory}:BrillouinZonePreviewPanelProps) {
  const reciprocalArtifact=findArtifact(artifacts,"reciprocal_lattice_json");
  const zoneArtifact=findArtifact(artifacts,"brillouin_zone_json");
  const kpathArtifact=findArtifact(artifacts,"kpath_json");
  const manifestArtifact=findArtifact(artifacts,"brillouin_zone_manifest_json");
  const summaryArtifact=findArtifact(artifacts,"summary_md");
  const recipeArtifact=findArtifact(artifacts,"recipe_json");
  const [active,setActive]=useState<PreviewTab>("renderer");
  const bundle=useMemo(()=>({reciprocal:payload(reciprocalArtifact),zone:payload(zoneArtifact),kpath:kpathArtifact?payload(kpathArtifact):undefined,manifest:payload(manifestArtifact)}),[reciprocalArtifact,zoneArtifact,kpathArtifact,manifestArtifact]);
  if(!reciprocalArtifact&&!zoneArtifact&&!manifestArtifact)return null;
  const entries=[
    ["倒易晶格",payload(reciprocalArtifact)],
    ["布里渊区",payload(zoneArtifact)],
    ["k 路径",kpathArtifact?payload(kpathArtifact):null],
  ] as const;
  return <section className="panel viewer-static-preview brillouin-zone-preview" data-testid="brillouin-zone-preview-panel">
    <div className="brillouin-zone-product-heading"><div><h2>布里渊区</h2><p>基于已验证倒易空间数据的三维查看器。</p></div><span>独立倒易空间视图</span></div>
    <div className="viewer-preview-tabs" role="tablist" aria-label="布里渊区查看模式">
      <button type="button" role="tab" aria-selected={active==="renderer"} className={active==="renderer"?"active":"secondary"} onClick={()=>setActive("renderer")}>三维查看</button>
      <button type="button" role="tab" aria-selected={active==="data"} className={active==="data"?"active":"secondary"} onClick={()=>setActive("data")}>科学数据</button>
      <button type="button" role="tab" aria-selected={active==="manifest"} className={active==="manifest"?"active":"secondary"} onClick={()=>setActive("manifest")}>数据清单</button>
    </div>
    <div role="tabpanel" className="viewer-preview-tab-panel">
      {active==="renderer"?<BrillouinZoneSurface bundle={bundle} capabilityOverride={capabilityOverride} engineFactory={engineFactory} summary={textPayload(summaryArtifact)} recipe={payload(recipeArtifact)}/>:null}
      {active==="data"?<div className="brillouin-zone-json-grid">{entries.map(([label,value])=><details key={label} open={label==="布里渊区"}><summary>{label}</summary>{value?<pre className="json-preview">{JSON.stringify(value,null,2)}</pre>:<p className="empty-state">此数据未由当前已验证数据包提供。</p>}</details>)}</div>:null}
      {active==="manifest"?<pre className="json-preview" data-testid="brillouin-zone-manifest-json">{JSON.stringify(payload(manifestArtifact),null,2)}</pre>:null}
    </div>
  </section>;
}

function findArtifact(artifacts:readonly Artifact[],type:string){return artifacts.find((item)=>item.type===type);}
function payload(artifact:Artifact|undefined):unknown { if(!artifact)return null;const content=artifact.content??artifact.metadata;if(typeof content==="string")try{return JSON.parse(content);}catch{return content;}return content??artifact; }
function textPayload(artifact:Artifact|undefined):string|undefined { const value=payload(artifact);return typeof value==="string"?value:undefined; }
