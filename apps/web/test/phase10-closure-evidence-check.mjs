import { access, readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const evidence = path.join(root, "docs/phase10/evidence/phase10_closure_regression_pack");
const required = [
  "README.md", "test_inventory.json", "cross_phase_invariant_matrix.json", "tool_portfolio_results.json",
  "registry_planner_runtime_closure.json", "artifact_contract_closure.json", "viewer_product_composition.json",
  "legacy_compatibility_closure.json", "capability_truth.json", "deterministic_replay.json",
  "failure_fallback_matrix.json", "lifecycle_closure.json", "browser_matrix.json", "mobile_smoke.json",
  "security_audit.json", "network_audit.json", "artifact_hashes.json",
];

for (const file of required) await access(path.join(evidence, file));
const browser = JSON.parse(await readFile(path.join(evidence, "browser_matrix.json"), "utf-8"));
const results = browser.results || [];
for (const name of ["chromium", "firefox", "webkit"]) {
  const result = results.find((item) => item.browser === name);
  if (!result?.available || result.desktop?.state !== "rendered") throw new Error(`Phase 10 ${name} closure is not rendered`);
  if (result.external_request_count !== 0) throw new Error(`Phase 10 ${name} closure made external requests`);
  if ((result.console_errors || []).length !== 0 || (result.page_errors || []).length !== 0) throw new Error(`Phase 10 ${name} closure has console errors`);
}
const security = JSON.parse(await readFile(path.join(evidence, "security_audit.json"), "utf-8"));
const network = JSON.parse(await readFile(path.join(evidence, "network_audit.json"), "utf-8"));
const manifest = JSON.parse(await readFile(path.join(evidence, "evidence_manifest.json"), "utf-8"));
const hashes = JSON.parse(await readFile(path.join(evidence, "artifact_hashes.json"), "utf-8"));
if (security.result !== "PASS" || !security.markers?.includes("NO_SECRET_PATTERN_HITS")) throw new Error("Phase 10 security closure failed");
if (network.external_requests !== 0 || network.result !== "NO_EXTERNAL_NETWORK_REQUESTS") throw new Error("Phase 10 network closure failed");
if (manifest.schema_version !== "phase10.closure_regression_evidence.v1" || !manifest.markers?.includes("PHASE10_PRODUCT_CLOSURE_BROWSER_PASS")) throw new Error("Phase 10 evidence manifest is invalid");
if (hashes.algorithm !== "sha256" || !Array.isArray(hashes.files) || hashes.files.length < required.length) throw new Error("Phase 10 artifact hash inventory is invalid");
for (const item of hashes.files) {
  let content = await readFile(path.join(evidence, item.path));
  if (item.normalization === "lf") content = Buffer.from(content.toString("utf-8").replaceAll("\r\n", "\n"), "utf-8");
  else if (item.normalization !== "raw") throw new Error(`Phase 10 evidence hash normalization is invalid: ${item.path}`);
  if (content.byteLength !== item.bytes || createHash("sha256").update(content).digest("hex") !== item.sha256) throw new Error(`Phase 10 evidence hash mismatch: ${item.path}`);
}
console.log("PHASE10_CLOSURE_EVIDENCE_INTEGRITY_PASS");
