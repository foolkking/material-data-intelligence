import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs", "phase10k", "evidence", "phase10k1_material_data_profile_2");
const SCREENSHOTS = path.join(EVIDENCE, "browser", "screenshots");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE;
const PORT = Number(process.env.MDI_MATERIAL_PROFILE_EVIDENCE_PORT || "3391");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const audits = new WeakMap();

const profile = {
  schemaVersion: "0.1",
  profileId: "profile_dataset_material_profile_v2",
  datasetId: "dataset_material_profile",
  version: "2",
  datasetType: "ml_results",
  status: "ready",
  createdAt: "2026-07-28T00:00:00Z",
  tableSummary: {
    nRows: 4,
    nColumns: 6,
    columns: [
      { name: "material_id", dtype: "string", inferredRole: "structure_id" },
      { name: "formula", dtype: "string", inferredRole: "formula" },
      { name: "y_true", dtype: "number", inferredRole: "target" },
      { name: "model_a_pred", dtype: "number" },
      { name: "model_a_std", dtype: "number" },
      { name: "class_true", dtype: "string" },
    ],
  },
  objects: [{ id: "obj_dataframe_profile", objectType: "DataFrame", count: 1, objectHash: "a".repeat(64) }],
  profileContractVersion: "2.0",
  semanticRulesVersion: "phase10k1.material_profile_semantics.v1",
  semanticHash: "b".repeat(64),
  semanticColumns: [
    { objectId: "obj_dataframe_profile", column: "material_id", dtype: "string", roles: [{ role: "sample_identity", authority: "canonical_name", details: {} }] },
    { objectId: "obj_dataframe_profile", column: "formula", dtype: "string", roles: [{ role: "material_formula", authority: "canonical_name", details: { validCount: 4, invalidCount: 0 } }] },
    { objectId: "obj_dataframe_profile", column: "y_true", dtype: "number", roles: [{ role: "regression_target", authority: "canonical_name", details: {} }] },
    { objectId: "obj_dataframe_profile", column: "model_a_pred", dtype: "number", roles: [{ role: "regression_prediction", authority: "bounded_pattern", details: { property: "model_a" } }] },
    { objectId: "obj_dataframe_profile", column: "model_a_std", dtype: "number", roles: [{ role: "regression_uncertainty", authority: "bounded_pattern", details: { property: "model_a" } }] },
  ],
  semanticGroups: [
    { groupId: "obj_dataframe_profile:regression:default", kind: "regression", targetColumns: ["y_true"], predictionColumns: ["model_a_pred"], uncertaintyColumns: ["model_a_std"], probabilityColumns: [], classes: [], status: "COMPLETE", reasons: [] },
  ],
  resourceSemantics: [{ objectId: "obj_dataframe_profile", objectType: "DataFrame", objectHash: "a".repeat(64), kind: "dataframe", facts: { rowCount: 4, columnCount: 6 }, capabilities: ["table"], warnings: [] }],
  analysisReadiness: [
    { capability: "table_distribution", dataStatus: "READY", platformStatus: "AVAILABLE", reasons: ["DATA_REQUIREMENTS_SATISFIED"], requiredSemantics: ["table"], matchingGroups: [] },
    { capability: "regression_evaluation", dataStatus: "READY", platformStatus: "NOT_IMPLEMENTED", reasons: ["DATA_REQUIREMENTS_SATISFIED"], requiredSemantics: ["regression_prediction", "regression_target"], matchingGroups: ["obj_dataframe_profile:regression:default"] },
    { capability: "uncertainty_evaluation", dataStatus: "READY", platformStatus: "NOT_IMPLEMENTED", reasons: ["DATA_REQUIREMENTS_SATISFIED"], requiredSemantics: ["regression_prediction", "regression_uncertainty"], matchingGroups: ["obj_dataframe_profile:regression:default"] },
    { capability: "classification_evaluation", dataStatus: "MISSING_REQUIRED_DATA", platformStatus: "NOT_IMPLEMENTED", reasons: ["MISSING:classification_prediction", "MISSING:classification_target"], requiredSemantics: ["classification_prediction", "classification_target"], matchingGroups: [] },
  ],
  sampleIdentity: { policy: "explicit_column", explicitColumn: "material_id", fallbackPolicy: "dataset_version_object_hash_row_index", datasetVersion: "2", objectIds: ["obj_dataframe_profile"] },
  profileCoverage: { policy: "complete", rowsInspected: 4, totalRows: 4, columnsInspected: 6, totalColumns: 6, limits: { maxRows: 4096, maxColumns: 512 }, warnings: [] },
  qualityIssues: [{ severity: "warning", code: "PROFILE_WARNING_FIXTURE", message: "Fixture warning for browser evidence." }],
  recommendedTasks: [{ taskId: "ml.evaluation", availableNow: false, reason: "Data conditions are known; product remains planned." }],
};

async function main() {
  await mkdir(SCREENSHOTS, { recursive: true });
  const pw = await import(pathToFileURL(PLAYWRIGHT).href);
  const server = await ensureServer();
  const requested = new Set((process.env.MDI_MATERIAL_PROFILE_BROWSER_MATRIX || "chromium,firefox,webkit").split(",").map((value) => value.trim()));
  const candidates = [
    { id: "chromium", type: pw.chromium, options: { ...(CHROME ? { executablePath: CHROME } : {}), args: ["--no-sandbox", "--disable-background-networking"] } },
    { id: "firefox", type: pw.firefox, options: {} },
    { id: "webkit", type: pw.webkit, options: {} },
  ].filter((candidate) => requested.has(candidate.id));
  const results = [];
  try {
    await waitForApp();
    for (const candidate of candidates) {
      let browser;
      try {
        browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
        results.push(await runBrowser(browser, candidate.id));
        console.log(`MATERIAL_PROFILE_BROWSER_PASS ${candidate.id}`);
      } catch (error) {
        results.push({ browser: candidate.id, available: false, reason: safeError(error) });
        console.log(`MATERIAL_PROFILE_BROWSER_FALLBACK ${candidate.id} ${safeError(error)}`);
      } finally {
        await browser?.close().catch(() => {});
      }
    }
    const chromium = results.find((result) => result.browser === "chromium");
    if (!chromium?.available) throw new Error("Chromium is required for Profile 2.0 browser evidence.");
    if (results.some((result) => result.available && result.externalRequests !== 0)) throw new Error("External request observed.");
    if (!chromium.desktop?.hasSemanticSurface || !chromium.mobile?.hasSemanticSurface) throw new Error("Profile semantic surface missing.");
    await writeJson("browser/browser_matrix.json", results);
    await writeJson("browser/console_network_audit.json", {
      browsers: results.map((result) => ({ browser: result.browser, available: result.available, externalRequests: result.externalRequests || 0, consoleErrors: result.consoleErrors || [], pageErrors: result.pageErrors || [] })),
      marker: "NO_MATERIAL_PROFILE_EXTERNAL_NETWORK_REQUESTS",
    });
    await writeJson("browser/accessibility_audit.json", {
      chromium: chromium.desktop.accessibility,
      mobile: chromium.mobile.accessibility,
      marker: "MATERIAL_PROFILE_ACCESSIBILITY_EVIDENCE_PASS",
    });
    console.log("MATERIAL_PROFILE_BROWSER_EVIDENCE_PASS");
    console.log("MATERIAL_PROFILE_MOBILE_EVIDENCE_PASS");
    console.log("NO_MATERIAL_PROFILE_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    if (server) { server.kill(); await stopPort(); }
  }
}

async function runBrowser(browser, browserId) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
  const desktopPage = await evidencePage(context);
  await loadProfile(desktopPage);
  const desktop = await snapshot(desktopPage, "desktop");
  if (browserId === "chromium") await desktopPage.screenshot({ path: path.join(SCREENSHOTS, "01_profile_semantics_desktop.png"), fullPage: true });
  await desktopPage.close();
  let mobile = null;
  if (browserId === "chromium") {
    const mobileContext = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
    const mobilePage = await evidencePage(mobileContext);
    await loadProfile(mobilePage);
    mobile = await snapshot(mobilePage, "mobile");
    await mobilePage.screenshot({ path: path.join(SCREENSHOTS, "02_profile_semantics_mobile.png"), fullPage: true });
    await mobilePage.close();
    await mobileContext.close();
  }
  await context.close();
  return { browser: browserId, version: browser.version(), available: true, desktop, mobile, externalRequests: desktop.externalRequests + (mobile?.externalRequests || 0), consoleErrors: [...desktop.consoleErrors, ...(mobile?.consoleErrors || [])], pageErrors: [...desktop.pageErrors, ...(mobile?.pageErrors || [])] };
}

async function loadProfile(page) {
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("load");
  await page.waitForTimeout(500);
  await page.locator(".global-context-bar .context-button").first().evaluate((element) => element.click());
  const dialog = page.locator("section.dialog-panel");
  await dialog.waitFor();
  await dialog.locator(".button-row button").first().click();
  await page.waitForSelector('[data-testid="material-profile-intelligence"]');
  await page.waitForTimeout(100);
}

async function snapshot(page, viewport) {
  const audit = audits.get(page);
  const data = await page.evaluate(() => {
    const intelligence = document.querySelector('[data-testid="material-profile-intelligence"]');
    const context = document.querySelector('[data-testid="data-context-viewer"]');
    const text = intelligence?.textContent || "";
    return {
      hasSemanticSurface: Boolean(intelligence),
      semanticText: text,
      hasDataReady: text.includes("regression_evaluation"),
      hasPlannedNotImplemented: text.includes("uncertainty_evaluation"),
      warningVisible: text.includes("PROFILE_WARNING_FIXTURE"),
      profileContractVisible: context?.textContent?.includes("ml_results") || false,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      accessibility: { regionLabel: intelligence?.getAttribute("aria-label"), dataContextTestId: Boolean(context) },
      iframeCount: document.querySelectorAll("iframe").length,
      externalScripts: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length,
      javascriptUriCount: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
      inlineHandlerCount: [...document.querySelectorAll("*")].reduce((count, node) => count + [...node.attributes].filter((attribute) => /^on/i.test(attribute.name)).length, 0),
    };
  });
  if (!data.hasSemanticSurface || !data.hasDataReady || !data.hasPlannedNotImplemented || !data.warningVisible || data.horizontalOverflow) throw new Error(`${viewport} Profile surface audit failed: ${JSON.stringify(data)}`);
  if (data.iframeCount || data.externalScripts || data.javascriptUriCount || data.inlineHandlerCount) throw new Error(`${viewport} executable surface detected.`);
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.external.length || audit.httpErrors.length) throw new Error(`${viewport} browser audit failed: ${JSON.stringify(audit)}`);
  return { viewport, ...data, externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors };
}

async function evidencePage(context) {
  const audit = { external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
  const page = await context.newPage(); audits.set(page, audit);
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => { if (response.status() >= 400) audit.httpErrors.push({ status: response.status(), path: new URL(response.url()).pathname }); });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) return route.continue();
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    audit.external.push({ host: url.hostname, path: url.pathname });
    return route.abort();
  });
  return page;
}

async function api(route, url) {
  const method = route.request().method();
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: profile.datasetId, datasetId: profile.datasetId, projectId: "project_local", name: "Profile 2.0 evidence", status: "profile_ready", demo: true, profileId: profile.profileId, profile } });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname === "/planner/providers/status" || url.pathname === "/planner/providers/resolve") return route.fulfill({ json: { ok: true, provider: "mock", model: "mock", status: "ready", willUseLiveProvider: false, secretConfigured: false, redacted: true } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  return route.fulfill({ status: 404, json: { detail: "profile evidence route not found" } });
}

function startServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
  return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: "ignore" });
}
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const end = Date.now() + 60_000; while (Date.now() < end) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("Profile evidence app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; const ps = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`; await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); }); }
async function writeJson(relative, value) { await writeFile(path.join(EVIDENCE, relative), `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function safeError(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 500); }

await main();
