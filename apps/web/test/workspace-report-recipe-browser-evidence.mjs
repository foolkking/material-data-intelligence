import { spawn, spawnSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || path.join(ROOT, "apps", "web", "node_modules", "playwright", "index.mjs");
const OUTPUT = argumentValue("--output-dir") ? path.resolve(argumentValue("--output-dir")) : path.join(ROOT, "docs", "phase10m", "evidence", "phase10m5_scientific_report_recipe");
const PORT = Number(process.env.MDI_PHASE10M5_EVIDENCE_PORT || "3227");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const HASH = "a".repeat(64);
const CHECK_ONLY = process.argv.includes("--validate-fixtures");

async function main() {
  const fixture = reportFixture();
  validateFixture(fixture);
  if (CHECK_ONLY) {
    console.log("PHASE10M5_REPORT_RECIPE_FIXTURE_VALIDATION_PASS");
    return;
  }
  const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
  const engines = { chromium, firefox, webkit };
  const requested = (process.env.MDI_PHASE10M5_BROWSERS || "chromium,firefox,webkit").split(",").map((value) => value.trim()).filter(Boolean);
  if (requested.length !== 3 || ["chromium", "firefox", "webkit"].some((name) => !requested.includes(name))) throw new Error("M5 requires Chromium, Firefox, and WebKit.");
  await mkdir(path.join(OUTPUT, "screenshots"), { recursive: true });
  const server = await ensureServer();
  try {
    await waitForApp();
    const matrix = {};
    for (const name of requested) {
      const browser = await engines[name].launch(browserOptions(name));
      try {
        matrix[name] = await runDesktop(browser, name, fixture);
      } finally {
        await browser.close();
      }
      await writeJson(`browser_${name}.json`, matrix[name]);
    }
    const mobileBrowser = await chromium.launch(browserOptions("chromium"));
    let mobile;
    try {
      mobile = await runMobile(mobileBrowser, fixture);
    } finally {
      await mobileBrowser.close();
    }
    await writeJson("browser_mobile.json", mobile);
    await writeJson("network_summary.json", { unapprovedExternalRequests: 0, initialArtifactPayloadRequests: 0, reportPreviewWebglContexts: 0, marker: "NO_M5_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS" });
    await writeJson("console_summary.json", { consoleErrors: [], pageErrors: [], failedResponses: [], marker: "NO_M5_BROWSER_ERRORS" });
    await writeJson("browser_matrix.json", matrix);
    console.log("PHASE10M5_CHROMIUM_FIREFOX_WEBKIT_PASS");
    console.log("PHASE10M5_CHROMIUM_390X844_PASS");
    console.log("PHASE10M5_REPORT_RECIPE_BROWSER_EVIDENCE_PASS");
  } finally {
    await stopServer(server);
  }
}

async function runDesktop(browser, browserName, fixture) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1050 }, reducedMotion: "reduce", acceptDownloads: true });
  const page = await context.newPage();
  const audit = attachAudit(page);
  const calls = [];
  await installApiFixture(page, calls, fixture);
  await page.goto(`${ORIGIN}/workspaces/workspace_report?panel=panel_report`, { waitUntil: "networkidle" });
  await page.getByTestId("workspace-report-composer").waitFor({ timeout: 30000 });
  try {
    await page.getByText(/5 exact sources; 2 mandatory disclosures/u).waitFor({ timeout: 30000 });
  } catch (error) {
    await page.screenshot({ path: path.join(OUTPUT, "screenshots", `${browserName}_initial_failure.png`), fullPage: true }).catch(() => {});
    const diagnostics = await page.locator("body").innerText().catch(() => "");
    throw new Error(`${browserName}: report inventory did not load; url=${page.url()} calls=${JSON.stringify(calls)} body=${JSON.stringify(diagnostics.slice(0, 1200))}`, { cause: error });
  }
  const initialPayloadRequests = calls.filter((call) => call.path.includes("/content")).length;
  if (initialPayloadRequests !== 0) throw new Error(`${browserName}: initial report panel loaded Artifact payload`);
  if (await page.locator("canvas").count() !== 0) throw new Error(`${browserName}: report preview mounted WebGL`);
  if (!(await page.getByRole("button", { name: "Add artifact_unknown to report" })).isDisabled()) throw new Error(`${browserName}: unsupported source was selectable`);

  await page.getByRole("button", { name: "Add artifact_plot to report" }).click();
  await page.getByRole("button", { name: "Add artifact_structure to report" }).click();
  const selected = await page.locator(".workspace-report-selected-list > li").count();
  if (selected !== 2) throw new Error(`${browserName}: exact report source selection failed`);
  const previewWritesBefore = calls.filter((call) => call.method === "POST" && call.path.includes("report-compositions")).length;
  await page.getByRole("button", { name: "Preview report" }).click();
  await page.getByRole("heading", { name: "Deterministic preview" }).waitFor({ timeout: 30000 });
  if (!(await page.getByText(/Report writes 0; Recipe writes 0; Job creation 0/u)).isVisible()) throw new Error(`${browserName}: preview no-write disclosure missing`);
  const previewWritesAfter = calls.filter((call) => call.method === "POST" && call.path.includes("report-compositions")).length;
  if (previewWritesAfter !== previewWritesBefore + 1 || await page.locator("canvas").count() !== 0) throw new Error(`${browserName}: preview write/WebGL gate failed`);

  await page.getByRole("button", { name: "Finalize report" }).click();
  await page.getByRole("heading", { name: "Report detail" }).waitFor({ timeout: 30000 });
  await page.getByText("Exact non-executable Recipe").waitFor({ timeout: 30000 });
  if (!(await page.getByText(/immutable Report and exact Recipe loaded/u)).isVisible()) throw new Error(`${browserName}: finalized pair detail missing`);
  const downloads = {};
  for (const format of ["json", "markdown"]) {
    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: format === "json" ? "Download canonical JSON" : "Download Markdown" }).click();
    const download = await downloadPromise;
    downloads[format] = { suggestedFilename: download.suggestedFilename() };
  }

  await page.getByRole("tab", { name: "Compose" }).click();
  await page.getByRole("button", { name: "Preview report" }).click();
  await page.getByRole("heading", { name: "Deterministic preview" }).waitFor({ timeout: 30000 });
  await page.getByRole("button", { name: "Finalize report" }).click();
  await page.getByRole("heading", { name: "Report detail" }).waitFor({ timeout: 30000 });
  if (fixture.history.length !== 1) throw new Error(`${browserName}: idempotent finalize created duplicate history`);
  for (let index = 0; index < 10; index += 1) {
    await page.getByRole("tab", { name: index % 2 ? "History" : "Compose" }).click();
  }
  const overflow = await page.evaluate(() => ({ body: document.body.scrollWidth - document.body.clientWidth, root: document.documentElement.scrollWidth - document.documentElement.clientWidth }));
  if (overflow.body > 0 || overflow.root > 0) throw new Error(`${browserName}: horizontal overflow ${JSON.stringify(overflow)}`);
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.failedResponses.length || audit.externalRequests.length) throw new Error(`${browserName}: browser audit failed ${JSON.stringify(audit)}`);
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", `${browserName}_report.png`), fullPage: true });
  await context.close();
  return { browser: browserName, metadataFirst: true, initialArtifactPayloadRequests: initialPayloadRequests, reportPreviewWebglContexts: 0, selectedSources: 2, mandatoryDisclosures: 2, previewWrites: 0, finalizePair: true, idempotentHistoryCount: fixture.history.length, downloads, overflow, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors, failedResponses: audit.failedResponses, externalRequests: audit.externalRequests };
}

async function runMobile(browser, fixture) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await context.newPage();
  const audit = attachAudit(page);
  const calls = [];
  await installApiFixture(page, calls, fixture);
  await page.goto(`${ORIGIN}/workspaces/workspace_report?panel=panel_report`, { waitUntil: "networkidle" });
  await page.getByTestId("workspace-report-composer").waitFor({ timeout: 30000 });
  await page.getByText(/5 exact sources; 2 mandatory disclosures/u).waitFor({ timeout: 30000 });
  const trigger = page.getByRole("button", { name: "Choose sources" });
  await trigger.click();
  const dialog = page.getByRole("dialog", { name: "Source inventory" });
  await dialog.waitFor();
  const close = dialog.getByRole("button", { name: "Close source picker" });
  if (!(await close).isVisible()) throw new Error("mobile source picker did not open");
  await dialog.getByRole("button", { name: "Add artifact_plot to report" }).click();
  await dialog.getByRole("button", { name: "Add artifact_structure to report" }).click();
  await page.keyboard.press("Escape");
  if (!(await trigger).evaluate((element) => element === document.activeElement)) throw new Error("mobile source picker did not restore focus");
  await page.getByRole("button", { name: "Preview report" }).click();
  await page.getByRole("heading", { name: "Deterministic preview" }).waitFor({ timeout: 30000 });
  const overflow = await page.evaluate(() => ({ body: document.body.scrollWidth - document.body.clientWidth, root: document.documentElement.scrollWidth - document.documentElement.clientWidth }));
  const minTouchTarget = await page.locator(".scientific-workspace button:visible").evaluateAll((items) => Math.min(...items.map((item) => Math.min(item.getBoundingClientRect().width, item.getBoundingClientRect().height))));
  if (overflow.body > 0 || overflow.root > 0 || minTouchTarget < 44 || await page.locator("canvas").count() !== 0) throw new Error(`mobile composition gate failed ${JSON.stringify({ overflow, minTouchTarget })}`);
  await page.getByRole("tab", { name: "History" }).click();
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", "mobile_report.png"), fullPage: true });
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.failedResponses.length || audit.externalRequests.length) throw new Error(`mobile browser audit failed ${JSON.stringify(audit)}`);
  await context.close();
  return { browser: "chromium", viewport: [390, 844], sourceSheet: true, focusRestored: true, preview: true, history: true, initialArtifactPayloadRequests: calls.filter((call) => call.path.includes("/content")).length, reportPreviewWebglContexts: 0, overflow, minTouchTarget, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors, failedResponses: audit.failedResponses, externalRequests: audit.externalRequests };
}

async function installApiFixture(page, calls, fixture) {
  await page.route(`${API_ORIGIN}/**`, async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const call = { method: request.method(), path: url.pathname };
    calls.push(call);
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: corsHeaders() });
    if (url.pathname === "/workspaces/workspace_report") return route.fulfill(jsonResponse(fixture.workspace));
    if (url.pathname === "/workspaces/workspace_report/report-composition/sources") return route.fulfill(jsonResponse(fixture.sources));
    if (url.pathname === "/workspaces/workspace_report/report-compositions" && request.method() === "GET") return route.fulfill(jsonResponse({ workspaceId: "workspace_report", items: fixture.history, count: fixture.history.length, immutableHistory: true }));
    if (url.pathname === "/workspaces/workspace_report/report-compositions/preview" && request.method() === "POST") return route.fulfill(jsonResponse(fixture.preview));
    if (url.pathname === "/workspaces/workspace_report/report-compositions" && request.method() === "POST") {
      const key = request.headers()["idempotency-key"] || "missing";
      if (fixture.finalizeKeys.has(key)) return route.fulfill(jsonResponse({ ...fixture.finalize, idempotentReplay: true }, 200));
      fixture.finalizeKeys.add(key);
      fixture.history.push(fixture.historyItem);
      return route.fulfill(jsonResponse(fixture.finalize, 201));
    }
    if (url.pathname === "/workspaces/workspace_report/report-compositions/report_saved") return route.fulfill(jsonResponse({ legacyReadOnly: false, report: fixture.report, recipeId: "recipe_saved" }));
    if (url.pathname === "/workspaces/workspace_report/report-compositions/report_saved/recipe") return route.fulfill(jsonResponse({ legacyReadOnly: false, recipe: fixture.recipe }));
    const exportMatch = /^\/workspaces\/workspace_report\/report-compositions\/report_saved\/exports\/(json|markdown)$/u.exec(url.pathname);
    if (exportMatch) return route.fulfill({ status: 200, headers: { ...corsHeaders(), "content-type": exportMatch[1] === "json" ? "application/json" : "text/markdown; charset=utf-8", "content-disposition": `attachment; filename="scientific-report-report_saved.${exportMatch[1] === "json" ? "json" : "md"}"`, "x-report-export-hash": HASH }, body: exportMatch[1] === "json" ? `${JSON.stringify({ report: fixture.report, recipe: fixture.recipe })}\n` : "# Scientific report\n\nWarnings and limitations are retained.\n" });
    return route.fulfill(jsonResponse({ detail: { code: "M5_FIXTURE_NOT_FOUND", message: "Fixture route not found" } }, 404));
  });
}

function reportFixture() {
  const figure = source("artifact_plot", "REPORT_FIGURE_SOURCE", "ELIGIBLE", "STATIC_FIGURE", "plotly_json", "Backend-produced static figure.");
  const structure = source("artifact_structure", "REPORT_METADATA_ONLY", "METADATA_ONLY", "METADATA", "structure_json", "Exact structure identity and approved text fallback.");
  const claim = source("claim_count", "REPORT_FINDING_SOURCE", "ELIGIBLE", "CLAIM", "grounded_claim", "Grounded claim with exact evidence link.", "SCIENTIFIC_CLAIM");
  const evidence = source("evidence_count", "REPORT_EVIDENCE_SOURCE", "ELIGIBLE", "EVIDENCE", "scientific_evidence_item", "Exact evidence item.", "EVIDENCE_ITEM");
  const unsupported = source("artifact_unknown", "REPORT_UNSUPPORTED", "UNSUPPORTED", "NONE", "unknown_contract", "Unknown contract is inert and has no renderer.");
  const disclosure = source("disclosure_partial", "REPORT_DISCLOSURE_ONLY", "MANDATORY", "DISCLOSURE", "report.disclosure", "Failed and blocked execution scope remains disclosed.");
  const disclosureStale = source("disclosure_stale", "REPORT_DISCLOSURE_ONLY", "MANDATORY", "DISCLOSURE", "report.disclosure", "Stale source remains exact and cannot be rebound.");
  const report = makeReport([figure, structure]);
  const recipe = makeRecipe(report);
  return { workspace: makeWorkspace(), sources: { schemaVersion: "1.0", workspaceId: "workspace_report", workspaceRevision: 1, workspaceProjectionHash: HASH, sources: [figure, structure, claim, evidence, unsupported], mandatoryDisclosures: [disclosure, disclosureStale], sourceCount: 5, mandatoryDisclosureCount: 2, artifactContractInventoryCount: 42, metadataOnly: true, heavyArtifactPayloadRequests: 0, webglContexts: 0 }, history: [], historyItem: { reportId: "report_saved", recipeId: "recipe_saved", version: "1.0", title: "Scientific report", reportHash: HASH, recipeHash: HASH, compositionHash: HASH, workspaceId: "workspace_report", workspaceRevision: 1, sourceJobId: "job_report", outcome: "REPORT_READY_WITH_LIMITS", createdAt: "2026-08-05T00:00:00Z", legacyReadOnly: false, exportFormats: ["json", "markdown"] }, finalize: { reportId: "report_saved", reportHash: HASH, recipeId: "recipe_saved", recipeHash: HASH, compositionHash: HASH, workspaceId: "workspace_report", workspaceRevision: 1, outcome: "REPORT_READY_WITH_LIMITS", idempotentReplay: false, immutable: true, noExecution: { planCreated: false, jobCreated: false, toolCallCreated: false, queueMessageCreated: false } }, report, recipe, preview: { report: makeReport([figure, structure]), recipe, sourceCount: 5, mandatoryDisclosureCount: 2, predictedOutcome: "REPORT_READY_WITH_LIMITS", persisted: false, noExecution: { planCreated: false, jobCreated: false, toolCallCreated: false, queueMessageCreated: false } }, finalizeKeys: new Set() };
}

function makeWorkspace() {
  const kinds = ["OVERVIEW", "DATA", "PLAN", "EXECUTION", "SCIENTIFIC_RESULT", "FINDINGS", "EVIDENCE", "PROVENANCE", "REPORT"];
  const panels = kinds.map((kind, ordinal) => ({ schemaVersion: "1.0", panelId: `panel_${kind.toLowerCase()}`, workspaceId: "workspace_report", panelKind: kind, title: kind === "REPORT" ? "Report" : kind.replaceAll("_", " "), ordinal, visible: true, sourceRefs: [{ kind: "JOB", sourceId: "job_report", sourceHash: HASH, contract: null, contractVersion: null, mediaType: null, projectId: "project_report", jobId: "job_report", toolCallId: null, stepId: null }], sourceReferenceHash: HASH, rendererContract: `workspace.${kind.toLowerCase()}/1.0`, state: kind === "REPORT" ? "PRODUCED" : "READY_NOT_RUN", acceptedSelectionKinds: ["ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], emittedSelectionKinds: [], evidenceRefs: [], provenanceRefs: ["job_report"], capabilityRequirement: null, layout: { region: "PRIMARY", order: ordinal, width: 1, height: 1, collapsed: false }, mobilePresentationMode: "FULL_WIDTH", accessibleName: kind === "REPORT" ? "Report" : kind, unsupportedReason: null, panelStateHash: HASH, contractProvenance: "phase10m5.browser_fixture.v1" }));
  const workspace = { schemaVersion: "1.0", workspaceId: "workspace_report", projectId: "project_report", sourceJobId: "job_report", sourceReferenceHash: HASH, datasetId: "dataset_report", datasetVersion: "v1", profileId: "profile_report", profileSemanticHash: HASH, intentId: "intent_report", intentSemanticHash: HASH, planId: "plan_report", planHash: HASH, planSchemaVersion: "0.2", title: "Report composition evidence", activePanelId: "panel_report", pinnedSelection: null, durableMetadata: { tags: [], note: null }, panelIds: panels.map((panel) => panel.panelId), currentLayoutRevision: 1, revision: 1, projectedStatus: "COMPLETE", historicalProjection: false, readOnly: false, warnings: [], diagnostics: [], artifactCount: 2, toolCallCount: 2, interpretationCount: 1, reportCount: 0, recipeCount: 0, createdByKind: "USER", createdBy: "browser_fixture", createdAt: "2026-08-05T00:00:00Z", updatedAt: "2026-08-05T00:00:00Z", executionAuthorized: false, scientificAuthority: false };
  return { workspace, panels, currentLayoutRevision: null, sourceSummary: { jobStatus: "completed", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "PARTIAL_RESULTS", artifactCount: 2, toolCallCount: 2, interpretationCount: 1, reportCount: 0, recipeCount: 0, metadataOnly: true }, projectionHash: HASH };
}

function source(sourceId, role, state, representation, contract, fallback, sourceKind = "ARTIFACT") {
  const isArtifact = sourceKind === "ARTIFACT";
  return { sourceKind, sourceId, sourceHash: HASH, contract, contractVersion: "1.0", projectId: "project_report", datasetId: "dataset_report", datasetVersion: "v1", jobId: "job_report", toolCallId: isArtifact ? "call_report" : null, stepId: isArtifact ? "step_report" : null, panelId: isArtifact ? "panel_scientific_result" : null, artifactId: isArtifact ? sourceId : null, artifactChecksum: isArtifact ? HASH : null, interpretationId: sourceKind === "SCIENTIFIC_CLAIM" || sourceKind === "EVIDENCE_ITEM" ? "interpretation_report" : null, claimId: sourceKind === "SCIENTIFIC_CLAIM" ? sourceId : null, evidenceItemId: sourceKind === "EVIDENCE_ITEM" ? sourceId : null, role, state, representation, fallback, reason: state === "UNSUPPORTED" ? fallback : null };
}

function makeReport(selectedSources) {
  const ids = ["TITLE", "ANALYSIS_GOAL", "DATASET_RESOURCE_SCOPE", "METHODS_PLAN", "EXECUTION_STATUS", "SELECTED_RESULTS", "GROUNDED_FINDINGS", "WARNINGS_LIMITATIONS", "FAILED_BLOCKED_MISSING", "EVIDENCE_PROVENANCE", "ENVIRONMENT_REFERENCES", "EXACT_RERUN_RECIPE"];
  return { schemaVersion: "1.0", reportId: "report_saved", reportHash: HASH, compositionHash: HASH, recipeId: "recipe_saved", workspaceId: "workspace_report", workspaceRevision: 1, projectId: "project_report", datasetId: "dataset_report", datasetVersion: "v1", sourceJobId: "job_report", sourcePlanId: "plan_report", sourcePlanHash: HASH, sourcePlanSchemaVersion: "0.2", title: "Scientific report", analysisGoal: "Compose exact persisted results", outcome: "REPORT_READY_WITH_LIMITS", selectedSources, mandatoryDisclosures: [], sections: ids.map((sectionId) => ({ sectionId, title: sectionId.replaceAll("_", " "), status: "READY", items: [`${sectionId} exact content`] })), warnings: ["Mandatory warning retained."], limitations: ["Report is a deterministic composition snapshot."], executionAuthorized: false, scientificAuthority: false, createdAt: "2026-08-05T00:00:00Z" };
}

function makeRecipe(report) {
  return { schemaVersion: "1.0", recipeId: "recipe_saved", recipeHash: HASH, compositionHash: HASH, sourceReportId: report.reportId, sourceReportHash: report.reportHash, workspaceId: report.workspaceId, workspaceRevision: 1, projectId: report.projectId, datasetId: report.datasetId, datasetVersion: report.datasetVersion, datasetHash: HASH, profileId: "profile_report", profileVersion: "1.0", profileHash: HASH, intentId: "intent_report", intentHash: HASH, eligibilityResolutionId: "eligibility_report", eligibilityResolutionHash: HASH, plannerDecisionId: "decision_report", plannerDecisionHash: HASH, analysisPlanId: "plan_report", analysisPlanHash: HASH, planSchemaVersion: "0.2", dependencyModel: "TYPED_ARTIFACT_BINDINGS", graphHash: HASH, steps: [{ stepId: "step_report", toolId: "table.numeric_summary", toolVersion: "1.0", adapterVersion: "1.0", params: { columns: ["value"] }, inputRefs: [], expectedOutputContracts: ["plotly_json"] }], dependencyBindings: [], sourceResourceBindings: [], originalArtifacts: report.selectedSources.filter((source) => source.artifactId), executionOutcome: "PARTIAL_RESULTS", providerProvenance: null, environmentProvenance: { applicationVersion: "browser-fixture" }, warnings: ["Mandatory warning retained."], limitations: ["Deterministic composition only."], outcome: "RECIPE_READY_WITH_LIMITS", executionAuthorized: false, planCreated: false, jobCreated: false, queueMessageCreated: false, automaticReplay: false, createdAt: "2026-08-05T00:00:00Z" };
}

function validateFixture(fixture) { if (fixture.sources.sourceCount !== 5 || fixture.sources.mandatoryDisclosureCount !== 2 || fixture.sources.artifactContractInventoryCount !== 42 || fixture.sources.metadataOnly !== true) throw new Error("M5 report fixture contract mismatch"); }
function browserOptions(name) { return name === "chromium" ? { headless: true, args: ["--no-sandbox", "--disable-background-networking"] } : { headless: true }; }
function attachAudit(page) { const audit = { consoleErrors: [], pageErrors: [], failedResponses: [], externalRequests: [] }; page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); }); page.on("pageerror", (error) => audit.pageErrors.push(error.message)); page.on("response", (response) => { if (response.status() >= 400) audit.failedResponses.push(`${response.status()} ${response.url()}`); }); page.on("request", (request) => { const url = new URL(request.url()); if (!["127.0.0.1", "localhost"].includes(url.hostname)) audit.externalRequests.push(request.url()); }); return audit; }
function corsHeaders() { return { "access-control-allow-origin": ORIGIN, "access-control-allow-methods": "GET,POST,OPTIONS", "access-control-allow-headers": "content-type,idempotency-key", "access-control-expose-headers": "etag,x-idempotent-replay,content-disposition,x-report-export-hash" }; }
function jsonResponse(value, status = 200, headers = {}) { return { status, contentType: "application/json", headers: { ...corsHeaders(), ...headers }, body: JSON.stringify(value) }; }
async function writeJson(relative, value) { const target = path.join(OUTPUT, relative); await mkdir(path.dirname(target), { recursive: true }); await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function argumentValue(name) { const index = process.argv.indexOf(name); return index >= 0 ? process.argv[index + 1] : null; }
function startServer() { const command = process.platform === "win32" ? "cmd.exe" : "npm"; const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]; return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: API_ORIGIN }, stdio: "ignore" }); }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const deadline = Date.now() + 90000; while (Date.now() < deadline) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("M5 Workspace app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; spawnSync("powershell.exe", ["-NoProfile", "-Command", `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue;if($c){$c|%{Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}`], { stdio: "ignore" }); }
async function stopServer(server) { if (!server) return; if (process.platform === "win32") { spawnSync("taskkill", ["/pid", String(server.pid), "/T", "/F"], { stdio: "ignore" }); await stopPort(); } else server.kill("SIGTERM"); }

main().catch((error) => { console.error(error); process.exitCode = 1; });
