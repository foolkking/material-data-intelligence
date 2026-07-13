import { access, readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../../..");
const evidence=path.join(root,"docs/phase10g/evidence/phase10g3_trajectory_performance_browser");
const required=[
  "README.md","formal_tool_registration.json","capability_contract.json","performance_budget_contract.json","performance_tier_matrix.json",
  "cache_metrics.json","pending_request_metrics.json","gpu_resource_metrics.json","playback_stress.json","rapid_seek_stress.json",
  "variable_lattice_stress.json","supercell_stress.json","context_loss_stress.json","artifact_switching_stress.json",
  "desktop_performance_matrix.json","mobile_performance_matrix.json","api_valid_fixed.json","api_many_frames.json","api_valid_variable.json",
  "api_degraded.json","api_refused.json","api_invalid.json","planner_routing.json","plan_validator_results.json",
  "browser_chromium.json","browser_firefox.json","browser_webkit.json","browser_mobile.json","accessibility_audit.json",
  "console_audit.json","network_audit.json","security_audit.json","evidence_manifest.json","artifact_hashes.json",
];
for(const file of required)await access(path.join(evidence,file));

const registration=await load("formal_tool_registration.json");
if(registration.tool_id!=="structure.trajectory_viewer"||registration.unique_count!==1||registration.network_access!==false)throw new Error("formal trajectory tool evidence invalid");
const capabilities=await load("capability_contract.json");
if(!capabilities.playback||!capabilities.variable_lattice||capabilities.dynamic_bonds!==false||capabilities.ensemble_rdf!==false||capabilities.editing!==false)throw new Error("trajectory capability truth invalid");
const budgets=await load("performance_budget_contract.json");
if(budgets.max_pending_requests!==1||budgets.max_prefetch_requests!==0||budgets.max_canvas_count!==1||budgets.max_context_count!==1)throw new Error("trajectory budgets invalid");

for(const [file,status,tier,artifacts] of [
  ["api_valid_fixed.json","completed","interactive",4],
  ["api_many_frames.json","completed","interactive",4],
  ["api_valid_variable.json","completed","interactive",4],
  ["api_degraded.json","completed","degraded",4],
  ["api_refused.json","completed","refused",4],
  ["api_invalid.json","failed",null,0],
]){
  const capture=await load(file);
  if(capture.capture_kind!=="real_in_memory_planner_job_runtime"||capture.worker.status!==status||capture.artifacts.length!==artifacts)throw new Error(`${file} API capture invalid`);
  if(artifacts){const provenance=capture.artifacts[0].metadata.provenance;if(provenance.toolId!=="structure.trajectory_viewer"||provenance.viewerLaunch.performanceMode!==tier)throw new Error(`${file} formal provenance invalid`);}
}

for(const browser of ["chromium","firefox","webkit"]){
  const result=await load(`browser_${browser}.json`);
  if(!result.available||result.fixed.recovered.viewer.canvasCount!==1||result.fixed.recovered.viewer.contextCount!==1||result.externalRequests!==0||result.consoleErrors.length||result.pageErrors.length)throw new Error(`${browser} trajectory browser evidence invalid`);
}
const mobile=await load("browser_mobile.json");
if(mobile.chromium.portraitViewport[0]>400||mobile.chromium.localOverflow.length||mobile.chromium.refusedCode!=="TRAJECTORY_VIEWER_BUDGET_EXCEEDED")throw new Error("mobile trajectory evidence invalid");
const accessibility=await load("accessibility_audit.json");
if(accessibility.liveRegion!=="polite"||accessibility.localOverflow.length||accessibility.horizontalOverflow)throw new Error("trajectory accessibility evidence invalid");
const network=await load("network_audit.json");
const security=await load("security_audit.json");
const manifest=await load("evidence_manifest.json");
if(network.externalRequests!==0||network.result!=="NO_EXTERNAL_NETWORK_REQUESTS"||security.result!=="PASS"||security.marker!=="NO_SECRET_PATTERN_HITS")throw new Error("trajectory network/security evidence invalid");
for(const marker of ["TRAJECTORY_FORMAL_API_EVIDENCE_PASS","TRAJECTORY_PERFORMANCE_BROWSER_EVIDENCE_PASS","TRAJECTORY_MOBILE_PERFORMANCE_EVIDENCE_PASS","NO_EXTERNAL_NETWORK_REQUESTS","NO_SECRET_PATTERN_HITS"])if(!manifest.markers.includes(marker))throw new Error(`missing trajectory evidence marker ${marker}`);

const hashes=await load("artifact_hashes.json");
if(hashes.algorithm!=="sha256"||!Array.isArray(hashes.files)||hashes.files.length<required.length)throw new Error("trajectory evidence hash inventory invalid");
for(const item of hashes.files){
  if(!["raw","lf"].includes(item.normalization))throw new Error(`unsupported trajectory hash normalization: ${item.path}`);
  const raw=await readFile(path.join(evidence,item.path));
  const content=item.normalization==="lf"?Buffer.from(raw.toString("utf-8").replace(/\r\n?/g,"\n"),"utf-8"):raw;
  if(content.byteLength!==item.bytes||createHash("sha256").update(content).digest("hex")!==item.sha256)throw new Error(`trajectory evidence hash mismatch: ${item.path}`);
}
console.log("TRAJECTORY_PERFORMANCE_EVIDENCE_INTEGRITY_PASS");

async function load(file){return JSON.parse(await readFile(path.join(evidence,file),"utf-8"));}
