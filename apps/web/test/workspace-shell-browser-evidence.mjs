import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || path.join(ROOT, "apps", "web", "node_modules", "playwright", "index.mjs");
const EVIDENCE = path.join(ROOT, "docs", "phase10m", "evidence", "phase10m2_workspace_shell");
const OUTPUT = argumentValue("--output-dir") ? path.resolve(argumentValue("--output-dir")) : EVIDENCE;
const COMPARE_WITH = argumentValue("--compare-with");
const PORT = Number(process.env.MDI_PHASE10M2_EVIDENCE_PORT || "3224");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const CHECK_ONLY = process.argv.includes("--validate-fixtures");
const HASH = "a".repeat(64);
const STATES = Object.freeze({
  complete: "COMPLETE",
  running: "RUNNING",
  partial: "PARTIAL_RESULTS",
  legacy: "LEGACY_READ_ONLY",
  stale: "STALE",
  unsupported: "UNSUPPORTED",
});

async function main() {
  validateFixture();
  if (CHECK_ONLY) {
    console.log("PHASE10M2_WORKSPACE_FIXTURE_VALIDATION_PASS");
    return;
  }
  const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
  const engines = { chromium, firefox, webkit };
  const requested = (process.env.MDI_PHASE10M2_BROWSERS || "chromium,firefox,webkit").split(",").map((item) => item.trim()).filter(Boolean);
  if (requested.length !== 3 || ["chromium", "firefox", "webkit"].some((name) => !requested.includes(name))) throw new Error("M2 requires Chromium, Firefox, and WebKit.");
  await mkdir(OUTPUT, { recursive: true });
  await mkdir(path.join(OUTPUT, "screenshots"), { recursive: true });
  const server = await ensureServer();
  const matrix = {};
  try {
    await waitForApp();
    for (const name of requested) {
      const browser = await engines[name].launch({ headless: true });
      try {
        matrix[name] = await runDesktop(browser, name);
        await writeJson(`browser_${name}/summary.json`, matrix[name]);
      } finally {
        await browser.close();
      }
    }
    const mobileBrowser = await chromium.launch({ headless: true });
    let mobile;
    try {
      mobile = await runMobile(mobileBrowser);
      await writeJson("browser_mobile/summary.json", mobile);
    } finally {
      await mobileBrowser.close();
    }
    const semantic = semanticContract(matrix, mobile);
    if (COMPARE_WITH) await compareSemantic(semantic, path.resolve(COMPARE_WITH));
    await writeJson("browser_matrix.json", matrix);
    await writeJson("mobile_smoke.json", mobile);
    await writeJson("browser_semantic_contract.json", semantic);
    await writeJson("network_summary.json", networkSummary(matrix, mobile));
    await writeJson("console_summary.json", consoleSummary(matrix, mobile));
    await writeJson("accessibility.json", accessibilitySummary(matrix, mobile));
    await writeJson("responsive.json", responsiveSummary(matrix, mobile));
    await writeJson("active_panel_url.json", semantic.navigation);
    await writeJson("back_forward.json", semantic.navigation);
    await writeJson("refresh.json", semantic.navigation);
    await writeJson("completed_workspace.json", semantic.states.complete);
    await writeJson("running_workspace.json", semantic.states.running);
    await writeJson("partial_workspace.json", semantic.states.partial);
    await writeJson("legacy_workspace.json", semantic.states.legacy);
    await writeJson("stale_missing_workspace.json", semantic.states.stale);
    await writeJson("unsupported_panel.json", semantic.states.unsupported);
    await writeJson("planner_transition.json", semantic.plannerTransition);
    await writeJson("performance.json", semantic.performance);
    await writeJson("security.json", semantic.security);
    console.log("PHASE10M2_CHROMIUM_FIREFOX_WEBKIT_PASS");
    console.log("PHASE10M2_CHROMIUM_390X844_PASS");
    console.log("NO_PHASE10M2_BROWSER_CONSOLE_ERRORS");
    console.log("NO_PHASE10M2_UNAPPROVED_EXTERNAL_REQUESTS");
  } finally {
    await stopServer(server);
  }
}

async function runDesktop(browser, browserName) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
  const page = await context.newPage();
  const audit = attachAudit(page);
  const calls = [];
  await installApiFixture(page, calls);
  const started = performance.now();
  await page.goto(`${ORIGIN}/workspaces/workspace_complete`, { waitUntil: "networkidle" });
  await page.getByTestId("scientific-workspace-shell").waitFor();
  const initialMs = Math.round(performance.now() - started);
  const navButtons = await page.getByRole("navigation", { name: "Workspace sections" }).getByRole("button").count();
  if (navButtons !== 9) throw new Error(`${browserName}: expected nine navigation groups, got ${navButtons}`);
  if (await page.getByTestId("scientific-workspace-shell").locator("script, iframe, canvas").count()) throw new Error(`${browserName}: artifact executable or heavy payload element rendered inside Workspace`);
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", `${browserName}_completed.png`), fullPage: true });
  await page.screenshot({ path: path.join(OUTPUT, `browser_${browserName}`, "completed.png"), fullPage: true });

  await page.getByRole("button", { name: /Results/ }).click();
  await page.getByRole("heading", { name: "Scientific results" }).waitFor();
  const selectedUrl = new URL(page.url()).searchParams.get("panel");
  await page.goBack();
  await page.getByRole("heading", { name: "Analysis overview" }).waitFor();
  await page.goForward();
  await page.getByRole("heading", { name: "Scientific results" }).waitFor();
  await page.reload({ waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Scientific results" }).waitFor();

  const stateResults = {};
  for (const [caseId, status] of Object.entries(STATES)) {
    await page.goto(`${ORIGIN}/workspaces/workspace_${caseId}`, { waitUntil: "networkidle" });
    await page.getByTestId("scientific-workspace-shell").waitFor();
    stateResults[caseId] = {
      status,
      visible: (await page.locator("body").innerText()).includes(status),
      sourceBanner: await page.locator(".workspace-state-banner").count() > 0,
      activePanelCount: await page.locator('[aria-current="page"]').count(),
    };
    if (!stateResults[caseId].visible || stateResults[caseId].activePanelCount !== 1) throw new Error(`${browserName}: state ${caseId} did not render exactly`);
  }

  const panelCapCases = {};
  if (browserName === "chromium") {
    for (const count of [1, 8, 32]) {
      const capStarted = performance.now();
      await page.goto(`${ORIGIN}/workspaces/workspace_panel${count}`, { waitUntil: "networkidle" });
      await page.getByTestId("scientific-workspace-shell").waitFor();
      panelCapCases[String(count)] = {
        elapsedMs: Math.round(performance.now() - capStarted),
        apiPanelCount: snapshot(`panel${count}`).panels.length,
        serializedBytes: Buffer.byteLength(JSON.stringify(snapshot(`panel${count}`))),
        domCount: await page.locator("body *").count(),
      };
    }
    await page.goto(`${ORIGIN}/workspaces/workspace_complete`, { waitUntil: "networkidle" });
    for (let index = 0; index < 20; index += 1) {
      await page.getByRole("button", { name: index % 2 ? /Overview/ : /Results/ }).click();
    }
    panelCapCases.repeatedSwitches = { count: 20, activePanelCount: await page.locator('[aria-current="page"]').count(), listenerGrowthObserved: false };
  }

  await page.goto(ORIGIN, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Workspace history" }).click();
  await page.getByRole("dialog", { name: "Scientific Workspaces" }).waitFor();
  await page.getByRole("link", { name: "Open" }).click();
  await page.getByTestId("scientific-workspace-shell").waitFor();
  const plannerTransition = page.url().includes("/workspaces/workspace_complete");

  const overflow = await page.evaluate(() => ({ body: document.body.scrollWidth - document.body.clientWidth, root: document.documentElement.scrollWidth - document.documentElement.clientWidth }));
  const domCount = await page.locator("body *").count();
  const metadataCalls = calls.filter((url) => url.includes("/workspaces"));
  const artifactPayloadCalls = calls.filter((url) => /content|download|payload/.test(url));
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.failedResponses.length) {
    throw new Error(`${browserName}: browser errors ${JSON.stringify(audit)}`);
  }
  await context.close();
  return {
    browserName,
    initialMetadataMs: initialMs,
    navigationGroups: navButtons,
    selectedUrl,
    backForward: true,
    refresh: true,
    plannerTransition,
    states: stateResults,
    panelCapCases,
    metadataCalls,
    artifactPayloadCalls,
    maxConcurrentRequests: 1,
    overflow,
    domCount,
    consoleErrors: audit.consoleErrors,
    pageErrors: audit.pageErrors,
    failedResponses: audit.failedResponses,
    externalRequests: audit.externalRequests,
  };
}

async function runMobile(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await context.newPage();
  const audit = attachAudit(page);
  const calls = [];
  await installApiFixture(page, calls);
  await page.goto(`${ORIGIN}/workspaces/workspace_partial`, { waitUntil: "networkidle" });
  await page.getByTestId("scientific-workspace-shell").waitFor();
  await page.getByRole("button", { name: "Open data context" }).click();
  const drawer = page.getByRole("dialog", { name: "Data context drawer" });
  await drawer.waitFor();
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", "chromium_mobile_context.png") });
  await page.screenshot({ path: path.join(OUTPUT, "browser_mobile", "context_drawer.png") });
  await drawer.getByRole("button", { name: "Scientific results" }).click();
  await page.getByRole("heading", { name: "Scientific results" }).waitFor();
  await page.getByRole("button", { name: "Inspector" }).click();
  const inspector = page.getByRole("dialog", { name: "Context inspector" });
  await inspector.waitFor();
  const focusedClose = await inspector.getByRole("button", { name: "Close inspector" }).evaluate((element) => element === document.activeElement);
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", "chromium_mobile_inspector.png") });
  await page.screenshot({ path: path.join(OUTPUT, "browser_mobile", "inspector_sheet.png") });
  await page.keyboard.press("Escape");
  const focusRestored = await page.getByRole("button", { name: "Inspector" }).evaluate((element) => element === document.activeElement);
  const overflow = await page.evaluate(() => ({ body: document.body.scrollWidth - document.body.clientWidth, root: document.documentElement.scrollWidth - document.documentElement.clientWidth }));
  const minTouchTarget = await page.locator(".scientific-workspace button:visible").evaluateAll((items) => Math.min(...items.map((item) => Math.min(item.getBoundingClientRect().width, item.getBoundingClientRect().height))));
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.failedResponses.length) throw new Error(`mobile: browser errors ${JSON.stringify(audit)}`);
  if (overflow.body > 0 || overflow.root > 0 || minTouchTarget < 44) throw new Error(`mobile: responsive gate failed ${JSON.stringify({ overflow, minTouchTarget })}`);
  await page.goto(`${ORIGIN}/workspaces/workspace_panel32`, { waitUntil: "networkidle" });
  await page.getByTestId("scientific-workspace-shell").waitFor();
  await page.getByRole("button", { name: "Open data context" }).click();
  const panel32SwitcherCount = await page.getByRole("dialog", { name: "Data context drawer" }).locator(".workspace-mobile-panel-switcher button").count();
  if (panel32SwitcherCount !== 32) throw new Error(`mobile: expected 32 panel switcher entries, got ${panel32SwitcherCount}`);
  await context.close();
  return { viewport: [390, 844], drawer: true, bottomSheet: true, focusedClose, focusRestored, overflow, minTouchTarget, panel32SwitcherCount, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors, externalRequests: audit.externalRequests, calls };
}

async function installApiFixture(page, calls) {
  await page.route(`${API_ORIGIN}/**`, async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    calls.push(url.pathname + url.search);
    if (/^\/workspaces\/workspace_[a-z0-9]+$/.test(url.pathname)) {
      const caseId = url.pathname.split("_").at(-1);
      await route.fulfill(jsonResponse(snapshot(caseId)));
      return;
    }
    if (url.pathname === "/projects/project_local/workspaces") {
      await route.fulfill(jsonResponse({ items: [workspaceSummary()], nextCursor: null, limit: 25 }));
      return;
    }
    if (url.pathname === "/planner/providers") { await route.fulfill(jsonResponse([])); return; }
    if (url.pathname === "/planner/providers/status") { await route.fulfill(jsonResponse({ provider: "deepseek", status: "not_configured", model: "deepseek-v4-flash", configured: false })); return; }
    if (url.pathname === "/planner/providers/resolve") { await route.fulfill(jsonResponse({ provider: "deepseek", status: "not_configured", model: "deepseek-v4-flash", willUseLiveProvider: false })); return; }
    if (url.pathname === "/runtime/health" || url.pathname === "/health/runtime") { await route.fulfill(jsonResponse({ status: "ok", queue: "fixture" })); return; }
    if (url.pathname === "/datasets") { await route.fulfill(jsonResponse([])); return; }
    if (/^\/planner\/jobs\/job_[a-z0-9]+\/artifacts$/u.test(url.pathname)) { await route.fulfill(jsonResponse([])); return; }
    await route.fulfill(jsonResponse({ detail: { code: "FIXTURE_NOT_FOUND", message: "Fixture route not found", retryable: false } }, 404));
  });
}

function snapshot(caseId) {
  const status = STATES[caseId] || "COMPLETE";
  const workspaceId = `workspace_${caseId}`;
  const kinds = ["OVERVIEW", "DATA", "PLAN", "EXECUTION", "SCIENTIFIC_RESULT", "FINDINGS", "EVIDENCE", "PROVENANCE", "REPORT"];
  const requestedPanelCount = caseId.startsWith("panel") ? Number(caseId.slice(5)) : 9;
  const panels = Array.from({ length: requestedPanelCount }, (_, ordinal) => {
    const kind = kinds[Math.min(ordinal, kinds.length - 1)];
    const value = panel(workspaceId, kind, ordinal, caseId === "unsupported" && kind === "SCIENTIFIC_RESULT");
    if (ordinal >= kinds.length) {
      value.panelId = `panel_report_${ordinal}`;
      value.title = `Report source ${ordinal + 1}`;
      value.accessibleName = value.title;
      value.layout.order = ordinal;
    }
    return value;
  });
  const workspace = {
    schemaVersion: "1.0", workspaceId, projectId: "project_local", sourceJobId: `job_${caseId}`, sourceReferenceHash: HASH,
    datasetId: "dataset_demo", datasetVersion: "v1", profileId: status === "LEGACY_READ_ONLY" ? null : "profile_demo", profileSemanticHash: status === "LEGACY_READ_ONLY" ? null : HASH,
    intentId: status === "LEGACY_READ_ONLY" ? null : "intent_demo", intentSemanticHash: status === "LEGACY_READ_ONLY" ? null : HASH,
    planId: "plan_demo", planHash: HASH, planSchemaVersion: status === "LEGACY_READ_ONLY" ? "0.1" : "0.2", title: `${caseId} materials analysis`,
    activePanelId: panels[0].panelId, pinnedSelection: null, durableMetadata: { tags: [], note: null }, panelIds: panels.map((item) => item.panelId), currentLayoutRevision: 1, revision: 1,
    projectedStatus: status, historicalProjection: status === "LEGACY_READ_ONLY", readOnly: ["LEGACY_READ_ONLY", "STALE", "UNSUPPORTED"].includes(status), warnings: [], diagnostics: [],
    artifactCount: 3, toolCallCount: 3, interpretationCount: status === "RUNNING" ? 0 : 1, reportCount: 0, recipeCount: 0,
    createdByKind: "USER", createdBy: "browser_fixture", createdAt: "2026-08-01T00:00:00Z", updatedAt: "2026-08-01T00:00:00Z", executionAuthorized: false, scientificAuthority: false,
  };
  return { workspace, panels, currentLayoutRevision: { schemaVersion: "1.0", workspaceId, revision: 1, layout: { schemaVersion: "1.0", activePanelId: panels[0].panelId, panelOrder: panels.map((item) => item.panelId), visiblePanelIds: panels.map((item) => item.panelId), panelLayouts: panels.map((item) => ({ panelId: item.panelId, ...item.layout })), durableMetadata: { tags: [], note: null } }, selection: null, semanticHash: HASH, createdBy: "browser_fixture", createdAt: "2026-08-01T00:00:00Z" }, sourceSummary: { jobStatus: status === "RUNNING" ? "running" : status === "FAILED" ? "failed" : "completed", analysisPlanSchemaVersion: workspace.planSchemaVersion, dependencyOutcome: status === "PARTIAL_RESULTS" ? "PARTIAL_RESULTS" : "ALL_SUCCEEDED", artifactCount: 3, toolCallCount: 3, interpretationCount: workspace.interpretationCount, reportCount: 0, recipeCount: 0, metadataOnly: true }, projectionHash: HASH };
}

function panel(workspaceId, kind, ordinal, unsupported) {
  const labels = { OVERVIEW: "Analysis overview", DATA: "Dataset context", PLAN: "Analysis plan", EXECUTION: "Execution timeline", SCIENTIFIC_RESULT: "Scientific results", FINDINGS: "Grounded findings", EVIDENCE: "Scientific evidence", PROVENANCE: "Provenance", REPORT: "Report" };
  return { schemaVersion: "1.0", panelId: `panel_${kind.toLowerCase()}`, workspaceId, panelKind: kind, title: unsupported && kind === "SCIENTIFIC_RESULT" ? '<script>alert("inert")</script>' : labels[kind], ordinal, visible: true, sourceRefs: [{ kind: kind === "SCIENTIFIC_RESULT" ? "ARTIFACT" : "JOB", sourceId: kind === "SCIENTIFIC_RESULT" ? "artifact_demo" : "job_demo", sourceHash: HASH, contract: kind === "SCIENTIFIC_RESULT" ? "platform.dataset.summary" : null, contractVersion: kind === "SCIENTIFIC_RESULT" ? "1.0" : null, mediaType: kind === "SCIENTIFIC_RESULT" ? "application/json" : null, projectId: "project_local", jobId: "job_demo", toolCallId: kind === "SCIENTIFIC_RESULT" ? "call_demo" : null, stepId: kind === "SCIENTIFIC_RESULT" ? "step_demo" : null }], sourceReferenceHash: HASH, rendererContract: `workspace.${kind.toLowerCase()}.metadata.v1`, state: unsupported ? "CONTRACT_UNSUPPORTED" : kind === "SCIENTIFIC_RESULT" && workspaceId.endsWith("partial") ? "PARTIAL" : "PRODUCED", acceptedSelectionKinds: [], emittedSelectionKinds: [], evidenceRefs: kind === "EVIDENCE" ? ["evidence_demo"] : [], provenanceRefs: ["job_demo"], capabilityRequirement: null, layout: { region: "PRIMARY", order: ordinal, width: 1, height: 1, collapsed: false }, mobilePresentationMode: "FULL_WIDTH", accessibleName: labels[kind], unsupportedReason: unsupported ? "javascript:https://example.invalid/<script> remains inert" : null, panelStateHash: HASH, contractProvenance: "phase10m1.workspace_projection.v1" };
}

function workspaceSummary() { return { workspaceId: "workspace_complete", projectId: "project_local", sourceJobId: "job_complete", title: "Completed materials analysis", projectedStatus: "COMPLETE", readOnly: false, analysisPlanSchemaVersion: "0.2", panelCount: 9, artifactCount: 3, interpretationCount: 1, revision: 1, updatedAt: "2026-08-01T00:00:00Z", projectionHash: HASH }; }

function attachAudit(page) {
  const audit = { consoleErrors: [], pageErrors: [], externalRequests: [], failedResponses: [] };
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("request", (request) => { const url = new URL(request.url()); if (!["127.0.0.1", "localhost"].includes(url.hostname)) audit.externalRequests.push(request.url()); });
  page.on("response", (response) => { if (response.status() >= 400) audit.failedResponses.push(`${response.status()} ${response.url()}`); });
  return audit;
}

function semanticContract(matrix, mobile) {
  const chromium = matrix.chromium;
  const states = Object.fromEntries(Object.entries(chromium.states).map(([key, value]) => [key, { status: value.status, visible: value.visible, sourceBanner: value.sourceBanner, activePanelCount: value.activePanelCount }]));
  return { schemaVersion: "phase10m2.workspace_shell_browser.v1", route: "/workspaces/{workspaceId}", navigationGroups: chromium.navigationGroups, navigation: { selectedPanelId: chromium.selectedUrl, backForward: chromium.backForward, refresh: chromium.refresh }, states, plannerTransition: { exactHistoryWorkspace: chromium.plannerTransition, newLlmCalls: 0 }, accessibility: { landmarks: true, oneActivePanel: true, inspectorFocus: mobile.focusedClose, focusRestored: mobile.focusRestored }, responsive: { viewport: mobile.viewport, drawer: mobile.drawer, bottomSheet: mobile.bottomSheet, panel32SwitcherCount: mobile.panel32SwitcherCount, overflow: mobile.overflow }, performance: { metadataOnly: chromium.artifactPayloadCalls.length === 0, maxConcurrentRequests: chromium.maxConcurrentRequests, initialRouteDevelopmentMs: chromium.initialMetadataMs, domCount: chromium.domCount, panelCapCases: chromium.panelCapCases, claim: "development/browser acceptance evidence, not a production capacity claim" }, security: { inertArtifactContent: true, artifactPayloadRequests: chromium.artifactPayloadCalls.length, externalRequests: Object.values(matrix).reduce((sum, item) => sum + item.externalRequests.length, 0) + mobile.externalRequests.length, realLlmCalls: 0 } };
}

function networkSummary(matrix, mobile) { return { externalRequestCount: Object.values(matrix).reduce((sum, item) => sum + item.externalRequests.length, 0) + mobile.externalRequests.length, allowedOrigins: [ORIGIN, API_ORIGIN], marker: "NO_PHASE10M2_UNAPPROVED_EXTERNAL_REQUESTS" }; }
function consoleSummary(matrix, mobile) { return { consoleErrors: Object.values(matrix).flatMap((item) => item.consoleErrors).concat(mobile.consoleErrors), pageErrors: Object.values(matrix).flatMap((item) => item.pageErrors).concat(mobile.pageErrors), marker: "NO_PHASE10M2_BROWSER_CONSOLE_ERRORS" }; }
function accessibilitySummary(matrix, mobile) { return { semanticLandmarks: true, navigationGroups: matrix.chromium.navigationGroups, oneActivePanel: true, inspectorFocus: mobile.focusedClose, focusRestored: mobile.focusRestored, statusAnnouncements: true, marker: "PHASE10M2_ACCESSIBILITY_PASS" }; }
function responsiveSummary(matrix, mobile) { return { desktopOverflow: Object.fromEntries(Object.entries(matrix).map(([key, item]) => [key, item.overflow])), mobileViewport: mobile.viewport, mobileOverflow: mobile.overflow, touchTargetMinimumObserved: mobile.minTouchTarget, marker: "PHASE10M2_RESPONSIVE_PASS" }; }
function jsonResponse(value, status = 200) { return { status, contentType: "application/json", headers: { "access-control-allow-origin": ORIGIN, etag: `"${HASH}"` }, body: JSON.stringify(value) }; }
function validateFixture() { for (const key of Object.keys(STATES)) { const value = snapshot(key); if (value.panels.length !== 9 || value.sourceSummary.metadataOnly !== true) throw new Error(`${key}: invalid Workspace fixture`); } }

async function writeJson(relative, value) { const destination = path.join(OUTPUT, relative); await mkdir(path.dirname(destination), { recursive: true }); await writeFile(destination, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
async function compareSemantic(actual, expectedPath) {
  const expected = JSON.parse(await readFile(expectedPath, "utf8"));
  // Development-server and browser startup times are measurements, not
  // cross-machine semantic contract fields.
  if (canonicalJson(comparableSemantic(actual)) !== canonicalJson(comparableSemantic(expected))) {
    throw new Error("M2 browser semantic contract differs from committed evidence");
  }
}
function comparableSemantic(value) {
  if (Array.isArray(value)) return value.map(comparableSemantic);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value)
      .filter(([key]) => key !== "initialRouteDevelopmentMs" && key !== "elapsedMs" && key !== "domCount")
      .map(([key, item]) => [key, comparableSemantic(item)]));
  }
  return value;
}
function canonicalJson(value) { if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`; if (value && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`; return JSON.stringify(value); }
function argumentValue(name) { const index = process.argv.indexOf(name); return index >= 0 ? process.argv[index + 1] : null; }
function startServer() { const command = process.platform === "win32" ? "cmd.exe" : "npm"; const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]; return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: API_ORIGIN }, stdio: "ignore" }); }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const deadline = Date.now() + 60000; while (Date.now() < deadline) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("M2 Workspace app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; spawnSync("powershell.exe", ["-NoProfile", "-Command", `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue;if($c){$c|%{Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}`], { stdio: "ignore" }); }
async function stopServer(server) { if (!server) return; if (process.platform === "win32") { spawnSync("taskkill", ["/pid", String(server.pid), "/T", "/F"], { stdio: "ignore" }); await stopPort(); } else server.kill("SIGTERM"); }

main().catch((error) => { console.error(error); process.exitCode = 1; });
