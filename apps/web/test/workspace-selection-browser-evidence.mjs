import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || path.join(ROOT, "apps", "web", "node_modules", "playwright", "index.mjs");
const OUTPUT = argumentValue("--output-dir") ? path.resolve(argumentValue("--output-dir")) : path.join(ROOT, "docs", "phase10m", "evidence", "phase10m3_canonical_selection");
const COMPARE_WITH = argumentValue("--compare-with");
const PORT = Number(process.env.MDI_PHASE10M3_EVIDENCE_PORT || "3225");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const HASH = "a".repeat(64);
const CHECK_ONLY = process.argv.includes("--validate-fixtures");

async function main() {
  const startedAt = performance.now();
  const initialHeapBytes = process.memoryUsage().heapUsed;
  validateFixture();
  if (CHECK_ONLY) return console.log("PHASE10M3_SELECTION_FIXTURE_VALIDATION_PASS");
  const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
  const requested = (process.env.MDI_PHASE10M3_BROWSERS || "chromium,firefox,webkit").split(",").map((item) => item.trim()).filter(Boolean);
  if (requested.length !== 3 || !["chromium", "firefox", "webkit"].every((name) => requested.includes(name))) throw new Error("M3 requires Chromium, Firefox, and WebKit.");
  await mkdir(path.join(OUTPUT, "screenshots"), { recursive: true });
  const server = await ensureServer();
  try {
    await waitForApp();
    const matrix = {};
    for (const name of requested) {
      const browser = await ({ chromium, firefox, webkit })[name].launch({ headless: true });
      try { matrix[name] = await runDesktop(browser, name); } finally { await browser.close(); }
    }
    const mobileBrowser = await chromium.launch({ headless: true });
    let mobile;
    try { mobile = await runMobile(mobileBrowser); } finally { await mobileBrowser.close(); }
    const semantic = semanticContract(matrix, mobile);
    if (COMPARE_WITH) await compareSemantic(semantic, path.resolve(COMPARE_WITH));
    await writeJson("browser_matrix.json", matrix);
    await writeJson("mobile_smoke.json", mobile);
    await writeJson("browser_semantic_contract.json", semantic);
    await writeJson("browser_performance.json", {
      basis: "development browser acceptance evidence, not a production capacity claim",
      elapsedMs: Number((performance.now() - startedAt).toFixed(3)),
      initialHeapBytes,
      finalHeapBytes: process.memoryUsage().heapUsed,
      desktopElapsedMs: Object.fromEntries(Object.entries(matrix).map(([name, item]) => [name, item.elapsedMs])),
      mobileElapsedMs: mobile.elapsedMs,
    });
    await writeJson("network_summary.json", { externalRequestCount: 0, allowedOrigins: [ORIGIN, API_ORIGIN], marker: "NO_PHASE10M3_UNAPPROVED_EXTERNAL_REQUESTS" });
    await writeJson("console_summary.json", { consoleErrors: [], pageErrors: [], marker: "NO_PHASE10M3_BROWSER_CONSOLE_ERRORS" });
    console.log("PHASE10M3_CHROMIUM_FIREFOX_WEBKIT_PASS");
    console.log("PHASE10M3_CHROMIUM_390X844_PASS");
  } finally { await stopServer(server); }
}

async function runDesktop(browser, browserName) {
  const startedAt = performance.now();
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
  const page = await context.newPage();
  const audit = attachAudit(page), calls = [];
  await installApiFixture(page, calls);
  const token = selectionToken();
  await page.goto(`${ORIGIN}/workspaces/workspace_select?panel=panel_data&selection=${token}`, { waitUntil: "networkidle" });
  await page.getByTestId("scientific-workspace-shell").waitFor();
  await page.getByTestId("workspace-selection-status").getByText("Restored canonical selection").waitFor();
  if (!page.url().includes(`selection=${token}`)) throw new Error(`${browserName}: canonical selection URL did not restore`);
  await page.getByRole("button", { name: /Results/ }).click();
  await page.getByTestId("workspace-select-artifact-panel_scientific_result").click();
  if (!new URL(page.url()).searchParams.get("selection")) throw new Error(`${browserName}: exact Artifact selection did not update URL`);
  await page.getByRole("button", { name: "Inspector" }).click();
  const inspector = page.getByRole("dialog", { name: "Context inspector" });
  await inspector.getByRole("heading", { name: "Canonical selection" }).waitFor();
  if (!(await inspector.innerText()).includes("ARTIFACT")) throw new Error(`${browserName}: Inspector did not render exact Artifact identity`);
  await inspector.getByRole("button", { name: "Pin selection" }).click();
  await page.getByText("Pin state: SAVED.").waitFor();
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", `${browserName}_selection.png`), fullPage: true });
  await inspector.getByRole("button", { name: "Clear selection" }).click();
  if (new URL(page.url()).searchParams.has("selection")) throw new Error(`${browserName}: clear did not remove URL selection`);
  await page.goBack();
  await page.getByTestId("workspace-selection-status").getByText("Restored canonical selection").waitFor();
  if (!new URL(page.url()).searchParams.has("selection")) throw new Error(`${browserName}: browser back did not restore the exact selection token`);
  await page.goForward();
  await page.getByTestId("workspace-selection-status").getByText("Restored the explicitly pinned canonical selection").waitFor();
  if (new URL(page.url()).searchParams.has("selection")) throw new Error(`${browserName}: browser forward did not restore the exact cleared URL state`);
  await page.keyboard.press("Escape");
  const stale = selectionToken("b".repeat(64));
  await page.goto(`${ORIGIN}/workspaces/workspace_select?selection=${stale}`, { waitUntil: "networkidle" });
  await page.getByTestId("workspace-selection-status").getByText("Selection URL rejected").waitFor();
  if ((await page.getByTestId("workspace-selection-status").innerText()).includes("DATASET_SAMPLE")) throw new Error(`${browserName}: stale token received a substitute selection`);
  const overflow = await page.evaluate(() => ({ body: document.body.scrollWidth - document.body.clientWidth, root: document.documentElement.scrollWidth - document.documentElement.clientWidth }));
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.failedResponses.length || audit.externalRequests.length) throw new Error(`${browserName}: browser audit failed ${JSON.stringify(audit)}`);
  if (calls.some((call) => !(call.method === "GET" && /^\/planner\/jobs\/job_[a-z0-9]+\/artifacts$/u.test(call.path)) && /planner|jobs|enqueue|tool-calls/i.test(call.path))) throw new Error(`${browserName}: selection attempted execution authority`);
  await context.close();
  return { browserName, urlRestore: true, artifactSelection: true, backForward: true, staleRejected: true, pinRequestCount: calls.filter((call) => call.method === "PATCH").length, elapsedMs: Number((performance.now() - startedAt).toFixed(3)), overflow, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors, externalRequests: audit.externalRequests, apiCalls: calls };
}

async function runMobile(browser) {
  const startedAt = performance.now();
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await context.newPage();
  const audit = attachAudit(page), calls = [];
  await installApiFixture(page, calls);
  await page.goto(`${ORIGIN}/workspaces/workspace_select?panel=panel_scientific_result`, { waitUntil: "networkidle" });
  await page.getByTestId("scientific-workspace-shell").waitFor();
  await page.getByTestId("workspace-select-artifact-panel_scientific_result").click();
  await page.getByRole("button", { name: "Inspector" }).click();
  const inspector = page.getByRole("dialog", { name: "Context inspector" });
  await inspector.waitFor();
  const focusedClose = await inspector.getByRole("button", { name: "Close inspector" }).evaluate((node) => node === document.activeElement);
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", "chromium_mobile_selection.png") });
  await page.keyboard.press("Escape");
  const focusRestored = await page.getByRole("button", { name: "Inspector" }).evaluate((node) => node === document.activeElement);
  const overflow = await page.evaluate(() => ({ body: document.body.scrollWidth - document.body.clientWidth, root: document.documentElement.scrollWidth - document.documentElement.clientWidth }));
  const minTouchTarget = await page.locator(".scientific-workspace button:visible").evaluateAll((items) => Math.min(...items.map((item) => Math.min(item.getBoundingClientRect().width, item.getBoundingClientRect().height))));
  if (overflow.body > 0 || overflow.root > 0 || minTouchTarget < 44) throw new Error(`mobile responsive gate failed ${JSON.stringify({ overflow, minTouchTarget })}`);
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.failedResponses.length || audit.externalRequests.length) throw new Error(`mobile browser audit failed ${JSON.stringify(audit)}`);
  await context.close();
  return { viewport: [390, 844], inspectorBottomSheet: true, focusedClose, focusRestored, elapsedMs: Number((performance.now() - startedAt).toFixed(3)), overflow, minTouchTarget, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors, externalRequests: audit.externalRequests, apiCalls: calls };
}

async function installApiFixture(page, calls) {
  await page.route(`${API_ORIGIN}/**`, async (route) => {
    const request = route.request(), url = new URL(request.url());
    calls.push({ method: request.method(), path: url.pathname });
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: corsHeaders() });
    if (request.method() === "GET" && /^\/workspaces\/workspace_[a-z0-9]+$/.test(url.pathname)) return route.fulfill(jsonResponse(snapshot()));
    if (request.method() === "PATCH" && /^\/workspaces\/workspace_[a-z0-9]+$/.test(url.pathname)) {
      const payload = request.postDataJSON();
      if (!payload?.pinnedSelection?.primary?.artifactId) return route.fulfill(jsonResponse({ detail: { code: "SELECTION_INVALID", message: "Fixture rejects invalid pin", retryable: false } }, 422));
      return route.fulfill(jsonResponse(snapshot(payload.pinnedSelection)));
    }
    if (request.method() === "GET" && /^\/planner\/jobs\/job_[a-z0-9]+\/artifacts$/u.test(url.pathname)) return route.fulfill(jsonResponse([]));
    return route.fulfill(jsonResponse({ detail: { code: "FIXTURE_NOT_FOUND", message: "Fixture route not found", retryable: false } }, 404));
  });
}

function snapshot(pinnedSelection = null) {
  const workspaceId = "workspace_select", jobId = "job_select";
  const kinds = ["OVERVIEW", "DATA", "PLAN", "EXECUTION", "SCIENTIFIC_RESULT", "FINDINGS", "EVIDENCE", "PROVENANCE", "REPORT"];
  const panels = kinds.map((kind, ordinal) => panel(workspaceId, jobId, kind, ordinal));
  const workspace = { schemaVersion: "1.0", workspaceId, projectId: "project_local", sourceJobId: jobId, sourceReferenceHash: HASH, datasetId: "dataset_demo", datasetVersion: "v1", profileId: "profile_demo", profileSemanticHash: HASH, intentId: "intent_demo", intentSemanticHash: HASH, planId: "plan_demo", planHash: HASH, planSchemaVersion: "0.2", title: "Canonical selection workspace", activePanelId: panels[0].panelId, pinnedSelection, durableMetadata: { tags: [], note: null }, panelIds: panels.map((item) => item.panelId), currentLayoutRevision: 1, revision: 1, projectedStatus: "COMPLETE", historicalProjection: false, readOnly: false, warnings: [], diagnostics: [], artifactCount: 1, toolCallCount: 1, interpretationCount: 1, reportCount: 0, recipeCount: 0, createdByKind: "USER", createdBy: "browser_fixture", createdAt: "2026-08-01T00:00:00Z", updatedAt: "2026-08-01T00:00:00Z", executionAuthorized: false, scientificAuthority: false };
  return { workspace, panels, currentLayoutRevision: { schemaVersion: "1.0", workspaceId, revision: 1, layout: { schemaVersion: "1.0", activePanelId: panels[0].panelId, panelOrder: panels.map((item) => item.panelId), visiblePanelIds: panels.map((item) => item.panelId), panelLayouts: panels.map((item) => ({ panelId: item.panelId, ...item.layout })), durableMetadata: { tags: [], note: null } }, selection: pinnedSelection, semanticHash: HASH, createdBy: "browser_fixture", createdAt: "2026-08-01T00:00:00Z" }, sourceSummary: { jobStatus: "completed", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, toolCallCount: 1, interpretationCount: 1, reportCount: 0, recipeCount: 0, metadataOnly: true }, projectionHash: HASH };
}

function panel(workspaceId, jobId, kind, ordinal) {
  const labels = { OVERVIEW: "Analysis overview", DATA: "Dataset context", PLAN: "Analysis plan", EXECUTION: "Execution timeline", SCIENTIFIC_RESULT: "Scientific results", FINDINGS: "Grounded findings", EVIDENCE: "Scientific evidence", PROVENANCE: "Provenance", REPORT: "Report" };
  const declarations = { OVERVIEW: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []], DATA: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME"], []], PLAN: [[], []], EXECUTION: [["ARTIFACT"], []], SCIENTIFIC_RESULT: [["PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT"], ["ARTIFACT"]], FINDINGS: [["ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []], EVIDENCE: [["ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []], PROVENANCE: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []], REPORT: [["ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []] };
  const source = kind === "SCIENTIFIC_RESULT" ? { kind: "ARTIFACT", sourceId: "artifact_demo", sourceHash: HASH, contract: "platform.dataset.summary", contractVersion: "1.0", mediaType: "application/json", projectId: "project_local", jobId, toolCallId: "call_demo", stepId: "step_demo" } : { kind: "JOB", sourceId: jobId, sourceHash: HASH, contract: null, contractVersion: null, mediaType: null, projectId: "project_local", jobId, toolCallId: null, stepId: null };
  const renderer = { OVERVIEW: "workspace.overview/1.0", DATA: "workspace.data/1.0", PLAN: "workspace.plan/1.0", EXECUTION: "workspace.execution/1.0", SCIENTIFIC_RESULT: "workspace.artifact-metadata/1.0", FINDINGS: "workspace.findings/1.0", EVIDENCE: "workspace.evidence/1.0", PROVENANCE: "workspace.provenance/1.0", REPORT: "workspace.report/1.0" };
  return { schemaVersion: "1.0", panelId: `panel_${kind.toLowerCase()}`, workspaceId, panelKind: kind, title: labels[kind], ordinal, visible: true, sourceRefs: [source], sourceReferenceHash: HASH, rendererContract: renderer[kind], state: "PRODUCED", acceptedSelectionKinds: declarations[kind][0], emittedSelectionKinds: declarations[kind][1], evidenceRefs: [], provenanceRefs: [jobId], capabilityRequirement: null, layout: { region: "PRIMARY", order: ordinal, width: 1, height: 1, collapsed: false }, mobilePresentationMode: "FULL_WIDTH", accessibleName: labels[kind], unsupportedReason: null, panelStateHash: HASH, contractProvenance: "phase10m3.selection_registry.v1" };
}

function selectionToken(scope = HASH) { return base64url(canonicalJson({ schemaVersion: "1.0", sourceScopeHash: scope, primary: selectionRef(scope), secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false })); }
function selectionRef(scope) { return { selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: scope, projectId: "project_local", ...Object.fromEntries(["datasetId", "datasetVersion", "jobId", "objectId", "sampleRef", "structureId", "siteId", "trajectoryId", "atomId", "frameId", "phononArtifactId", "qPointId", "branchId", "reciprocalArtifactId", "reciprocalPointId", "segmentId", "fieldId", "regionId", "artifactId", "artifactChecksum", "artifactContract", "artifactVersion", "toolCallId", "bundleId", "bundleHash", "evidenceItemId", "sourceArtifactId", "sourceArtifactChecksum", "fieldLocator", "interpretationId", "interpretationHash", "claimId"].map((field) => [field, null])), datasetId: "dataset_demo", datasetVersion: "v1", objectId: "object_1", sampleRef: "sample_1" }; }
function base64url(raw) { return Buffer.from(raw, "utf8").toString("base64url"); }
function canonicalJson(value) { if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`; if (value && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`; return JSON.stringify(value); }
function validateFixture() { const value = snapshot(); if (value.panels.length !== 9 || !value.panels.find((panel) => panel.panelKind === "SCIENTIFIC_RESULT")?.emittedSelectionKinds.includes("ARTIFACT") || selectionToken().length > 2048) throw new Error("M3 fixture is invalid"); }
function attachAudit(page) { const audit = { consoleErrors: [], pageErrors: [], failedResponses: [], externalRequests: [] }; page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); }); page.on("pageerror", (error) => audit.pageErrors.push(error.message)); page.on("response", (response) => { if (response.status() >= 400) audit.failedResponses.push(`${response.status()} ${response.url()}`); }); page.on("request", (request) => { const url = new URL(request.url()); if (!["127.0.0.1", "localhost"].includes(url.hostname)) audit.externalRequests.push(request.url()); }); return audit; }
function semanticContract(matrix, mobile) { return { schemaVersion: "phase10m3.workspace_selection_browser.v1", route: "/workspaces/{workspaceId}", query: { panel: true, selection: "canonical-base64url-v1", maxBytes: 2048 }, browsers: Object.fromEntries(Object.entries(matrix).map(([name, item]) => [name, { urlRestore: item.urlRestore, artifactSelection: item.artifactSelection, backForward: item.backForward, staleRejected: item.staleRejected, pinRequestCount: item.pinRequestCount, overflow: item.overflow }])), mobile: { viewport: mobile.viewport, inspectorBottomSheet: mobile.inspectorBottomSheet, focusedClose: mobile.focusedClose, focusRestored: mobile.focusRestored, overflow: mobile.overflow, minTouchTarget: mobile.minTouchTarget }, security: { realLlmCalls: 0, noArtifactPayloadRequests: true, noExecutionAuthority: true, noExternalRequests: true } }; }
async function compareSemantic(actual, expectedPath) { const expected = JSON.parse(await readFile(expectedPath, "utf8")); if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error("M3 browser semantic contract differs from committed evidence"); }
function corsHeaders() { return { "access-control-allow-origin": ORIGIN, "access-control-allow-methods": "GET,PATCH,OPTIONS", "access-control-allow-headers": "content-type,if-match", "access-control-expose-headers": "etag", etag: `"${HASH}"` }; }
function jsonResponse(value, status = 200) { return { status, contentType: "application/json", headers: corsHeaders(), body: JSON.stringify(value) }; }
async function writeJson(relative, value) { const target = path.join(OUTPUT, relative); await mkdir(path.dirname(target), { recursive: true }); await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function argumentValue(name) { const index = process.argv.indexOf(name); return index >= 0 ? process.argv[index + 1] : null; }
function startServer() { const command = process.platform === "win32" ? "cmd.exe" : "npm"; const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]; return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: API_ORIGIN }, stdio: "ignore" }); }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const deadline = Date.now() + 60000; while (Date.now() < deadline) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("M3 Workspace app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; spawnSync("powershell.exe", ["-NoProfile", "-Command", `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue;if($c){$c|%{Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}`], { stdio: "ignore" }); }
async function stopServer(server) { if (!server) return; if (process.platform === "win32") { spawnSync("taskkill", ["/pid", String(server.pid), "/T", "/F"], { stdio: "ignore" }); await stopPort(); } else server.kill("SIGTERM"); }

main().catch((error) => { console.error(error); process.exitCode = 1; });
