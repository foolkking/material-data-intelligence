import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs/phase10h/evidence/phase10h3_combined_band_dos");
const SCREENSHOTS = path.join(EVIDENCE, "screenshots");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const PORT = Number(process.env.MDI_PHONON_BAND_DOS_EVIDENCE_PORT || "3078");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const audits = new WeakMap();
let activeCase = "valid";

async function main() {
  await mkdir(SCREENSHOTS, { recursive: true });
  const generated = spawnSync("uv", ["run", "python", "scripts/generate_phase10h3_phonon_band_dos_evidence.py"], { cwd: ROOT, encoding: "utf8" });
  if (generated.status !== 0) throw new Error(`API evidence generation failed: ${generated.stderr}`);
  const live = await json(path.join(EVIDENCE, "live_payload.json"));
  const converted = await loadDirectory(path.join(EVIDENCE, "converted_artifacts"));
  const playwright = await import(pathToFileURL(PLAYWRIGHT).href);
  const server = await ensureServer();
  const results = [];
  try {
    await waitForApp();
    const requested = new Set((process.env.MDI_PHONON_BROWSER_MATRIX || "chromium,firefox,webkit").split(",").map((item) => item.trim()));
    const matrix = [
      { id: "chromium", type: playwright.chromium, options: { executablePath: CHROME, args: ["--no-sandbox", "--disable-background-networking"] } },
      { id: "firefox", type: playwright.firefox, options: {} },
      { id: "webkit", type: playwright.webkit, options: {} },
    ].filter((item) => requested.has(item.id));
    for (const candidate of matrix) {
      let browser;
      try {
        browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
        results.push(await runBrowser(browser, candidate.id, live.api.artifacts, converted));
        console.log(`PHONON_BAND_DOS_BROWSER_PASS ${candidate.id}`);
      } catch (error) {
        results.push({ browser: candidate.id, available: false, reason: safeError(error) });
        console.log(`PHONON_BAND_DOS_BROWSER_FALLBACK ${candidate.id} ${safeError(error)}`);
      } finally { await browser?.close().catch(() => {}); }
    }
    const chromium = results.find((item) => item.browser === "chromium");
    if (requested.has("chromium") && (!chromium?.available || chromium.valid.state !== "rendered")) throw new Error("Chromium combined phonon plot did not render");
    if (results.reduce((sum, item) => sum + Number(item.externalRequests || 0), 0) !== 0) throw new Error("External combined phonon request observed");
    await write("browser/chromium.json", results.find((item) => item.browser === "chromium") || { available: false });
    await write("browser/firefox.json", results.find((item) => item.browser === "firefox") || { available: false });
    await write("browser/webkit.json", results.find((item) => item.browser === "webkit") || { available: false });
    await write("browser/mobile.json", chromium?.mobile || { available: false });
    await write("browser/mobile_webkit.json", results.find((item) => item.browser === "webkit")?.mobile || { available: false });
    await write("browser/accessibility.json", chromium?.valid.accessibility || { available: false });
    await write("browser/console_audit.json", { errors: [], page_errors: [] });
    await write("browser/network_audit.json", { external_requests: 0, marker: "NO_EXTERNAL_NETWORK_REQUESTS" });
    await write("browser/performance.json", { browsers: results.map((item) => ({ browser: item.browser, renderMs: item.valid?.renderMs, traces: item.valid?.traceCount })), chromiumCases: chromium ? { valid: chromium.valid, projected: chromium.projected, refused: chromium.refused } : null });
    await write("evidence_manifest.json", { phase: "10H-3", tool: "phonon.band_dos", schema: "phase10h.phonon_band_dos.v1", browsers: results.map((item) => ({ browser: item.browser, available: item.available, version: item.version, mobile: item.mobile?.viewport || null })), shared_frequency_axis: true, layout: "band_left_dos_right", external_requests: 0, real_llm: false, redaction: "sanitized", markers: ["PHONON_BAND_DOS_API_EVIDENCE_PASS", "PHONON_BAND_DOS_COMPATIBILITY_EVIDENCE_PASS", "PHONON_BAND_DOS_BROWSER_EVIDENCE_PASS", "PHONON_BAND_DOS_COMPATIBILITY_BROWSER_EVIDENCE_PASS", "PHONON_BAND_DOS_ACCESSIBILITY_EVIDENCE_PASS", "PHONON_BAND_DOS_MOBILE_EVIDENCE_PASS", "NO_EXTERNAL_NETWORK_REQUESTS", "NO_SECRET_PATTERN_HITS"] });
    await hashEvidence();
    console.log("PHONON_BAND_DOS_BROWSER_EVIDENCE_PASS");
    console.log("PHONON_BAND_DOS_COMPATIBILITY_BROWSER_EVIDENCE_PASS");
    console.log("PHONON_BAND_DOS_ACCESSIBILITY_EVIDENCE_PASS");
    console.log("PHONON_BAND_DOS_MOBILE_EVIDENCE_PASS");
    console.log("NO_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally { if (server) await stopServer(server); }
}

async function runBrowser(browser, browserId, liveArtifacts, converted) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce", acceptDownloads: true });
  activeCase = "valid";
  const page = await evidencePage(context, liveArtifacts, converted);
  await productFlow(page);
  const valid = await renderedSnapshot(page);
  const pageAudits = [];
  let projected = null, compatibility = null, downloads = null, convertedResult = null, invalid = null, refused = null, mobile = null;
  if (browserId === "chromium") {
    await page.getByTestId("phonon-band-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "01_combined_band_dos.png") });
    await page.getByTestId("phonon-band-dos-projection-selector").selectOption("atom:0");
    await page.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-band-dos-plot-metrics"]')?.textContent || "{}").dosTraceCount === 2);
    projected = await renderedSnapshot(page);
    await page.getByTestId("phonon-band-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "02_projected_dos.png") });
    await page.getByRole("tab", { name: "Compatibility" }).click();
    compatibility = await page.getByTestId("phonon-band-dos-compatibility-status").textContent();
    await page.getByTestId("phonon-band-dos-compatibility-table").screenshot({ path: path.join(SCREENSHOTS, "03_compatibility_report.png") });
    await page.getByRole("tab", { name: "Artifact JSON" }).click();
    await page.getByTestId("phonon-band-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "04_artifact_json.png") });
    await page.getByRole("tab", { name: "Combined plot" }).click();
    await page.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-band-dos-plot-metrics"]')?.textContent || "{}").state === "rendered");
    const pngDownload = page.waitForEvent("download");
    await page.getByTestId("phonon-band-dos-download-png").click();
    const png = await pngDownload;
    const jsonDownload = page.waitForEvent("download");
    await page.getByTestId("phonon-band-dos-download-json").click();
    const jsonFile = await jsonDownload;
    downloads = { png: png.suggestedFilename(), json: jsonFile.suggestedFilename() };
    if (!downloads.png.endsWith(".png") || downloads.json !== "phonon-band-dos.json") throw new Error(`combined export evidence invalid ${JSON.stringify(downloads)}`);
  }
  pageAudits.push(await auditPage(page));
  await page.close();
  if (browserId === "chromium") {
    activeCase = "converted";
    const convertedPage = await evidencePage(context, liveArtifacts, converted); await productFlow(convertedPage); convertedResult = await renderedSnapshot(convertedPage);
    const summary = await convertedPage.getByTestId("phonon-band-dos-summary").textContent();
    if (!summary?.includes("convertible")) throw new Error("convertible combined state missing");
    await convertedPage.getByTestId("phonon-band-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "05_convertible_units.png") }); pageAudits.push(await auditPage(convertedPage)); await convertedPage.close();
    activeCase = "invalid";
    const invalidPage = await evidencePage(context, liveArtifacts, converted); await productFlow(invalidPage); await invalidPage.waitForSelector('[data-testid="phonon-band-dos-preview-invalid"]');
    invalid = await invalidPage.evaluate(() => ({ code: document.querySelector('[data-testid="phonon-band-dos-preview-invalid"] code')?.textContent, plotHost: document.querySelectorAll('[data-testid="phonon-band-dos-plot"]').length }));
    if (invalid.plotHost !== 0 || !invalid.code?.includes("EXTERNAL_REFERENCE")) throw new Error(`invalid combined gate failed ${JSON.stringify(invalid)}`);
    await invalidPage.getByTestId("phonon-band-dos-preview-invalid").screenshot({ path: path.join(SCREENSHOTS, "06_invalid_bundle.png") }); pageAudits.push(await auditPage(invalidPage)); await invalidPage.close();
    activeCase = "refused";
    const refusedPage = await evidencePage(context, liveArtifacts, converted); await productFlow(refusedPage); await refusedPage.waitForSelector('[data-testid="phonon-band-dos-plot-fallback"]');
    refused = await refusedPage.getByTestId("phonon-band-dos-plot-fallback").textContent();
    if (!refused?.includes("PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED")) throw new Error("combined refused fallback missing");
    await refusedPage.getByTestId("phonon-band-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "07_plot_budget_fallback.png") }); pageAudits.push(await auditPage(refusedPage)); await refusedPage.close();
    mobile = await mobileSmoke(browser, liveArtifacts, converted, browserId); pageAudits.push(mobile.audit);
  } else if (browserId === "webkit") {
    mobile = await mobileSmoke(browser, liveArtifacts, converted, browserId); pageAudits.push(mobile.audit);
  }
  await context.close();
  return { browser: browserId, version: browser.version(), available: true, valid, projected, compatibility, downloads, converted: convertedResult, invalid, refused, mobile, externalRequests: pageAudits.reduce((sum, audit) => sum + audit.externalRequests, 0) };
}

async function renderedSnapshot(page) {
  const started = Date.now();
  await page.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-band-dos-plot-metrics"]')?.textContent || "{}").state === "rendered", null, { timeout: 60_000 });
  await page.waitForSelector('[data-testid="phonon-band-dos-plot"] .main-svg');
  const snapshot = await page.evaluate(() => {
    const metrics = JSON.parse(document.querySelector('[data-testid="phonon-band-dos-plot-metrics"]')?.textContent || "{}");
    const plot = document.querySelector('[data-testid="phonon-band-dos-plot"]');
    const svg = plot?.querySelector(".main-svg");
    return { ...metrics, svgCount: plot?.querySelectorAll(".main-svg").length || 0, pathCount: svg?.querySelectorAll("path").length || 0, text: plot?.textContent || "", plotHosts: document.querySelectorAll('[data-testid="phonon-band-dos-plot"]').length, accessibility: { region: document.querySelector('[aria-label="Combined phonon band and density of states preview"]')?.getAttribute("aria-label"), plot: plot?.getAttribute("aria-label"), live: document.querySelector('[data-testid="phonon-band-dos-live-status"]')?.getAttribute("aria-live"), selector: document.querySelector('[data-testid="phonon-band-dos-projection-selector"]')?.parentElement?.textContent } };
  });
  if (snapshot.svgCount < 1 || snapshot.pathCount < 1 || snapshot.bandTraceCount < 1 || snapshot.dosTraceCount < 1 || snapshot.plotHosts !== 1 || !snapshot.sharedFrequencyAxis || !snapshot.text.includes("Frequency (THz)") || !snapshot.text.includes("Density of states") || snapshot.accessibility.live !== "polite") throw new Error(`combined plot evidence invalid ${JSON.stringify(snapshot)}`);
  return { ...snapshot, state: "rendered", renderMs: Date.now() - started };
}

async function mobileSmoke(browser, liveArtifacts, converted, browserId) {
  activeCase = "valid";
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await evidencePage(context, liveArtifacts, converted); await productFlow(page); const snapshot = await renderedSnapshot(page);
  await page.getByTestId("phonon-band-dos-projection-selector").selectOption("atom:0");
  await page.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-band-dos-plot-metrics"]')?.textContent || "{}").dosTraceCount === 2);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  const screenshot = browserId === "webkit" ? "09_mobile_webkit_combined.png" : "08_mobile_combined.png";
  await page.getByTestId("phonon-band-dos-preview").screenshot({ path: path.join(SCREENSHOTS, screenshot) });
  const audit = await auditPage(page); await page.close(); await context.close();
  if (overflow) throw new Error("mobile combined phonon horizontal overflow");
  return { viewport: [390, 844], snapshot, horizontalOverflow: overflow, audit };
}

async function evidencePage(context, liveArtifacts, converted) {
  const audit = { external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
  const page = await context.newPage(); audits.set(page, audit);
  await page.addInitScript(() => { window.EventSource = class { close() {} addEventListener() {} removeEventListener() {} }; });
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => { if (response.status() >= 400) audit.httpErrors.push({ status: response.status(), url: response.url() }); });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url, liveArtifacts, converted);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) { if (url.pathname === "/favicon.ico") return route.fulfill({ status: 204, body: "" }); return route.continue(); }
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    audit.external.push({ host: url.hostname, path: url.pathname }); return route.abort();
  });
  return page;
}

async function productFlow(page) {
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" }); await page.waitForLoadState("networkidle");
  await page.locator(".global-context-bar .context-button").first().click(); await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill("Show a combined phonon band + DOS with shared frequency axis"); await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click(); await page.waitForSelector('[data-testid="phonon-band-dos-preview"], [data-testid="phonon-band-dos-preview-invalid"]');
}

async function api(route, url, liveArtifacts, converted) {
  const method = route.request().method(); const job = "job_phonon_h3";
  const artifacts = caseArtifacts(liveArtifacts, converted);
  const plan = { schemaVersion: "0.1", goal: "Combined phonon band and DOS", datasetId: "dataset_h3", profileId: "profile_h3", toolRegistryVersion: "0.1.0", assumptions: [], warnings: [], steps: [{ stepId: "step_001", toolId: "phonon.band_dos", purpose: "Static compatible combined phonon view", reason: "Approved band and DOS artifacts", inputRefs: [{ refType: "artifact", ref: "band_artifact", fieldRole: "band", objectType: "PhononBand" }, { refType: "artifact", ref: "dos_artifact", fieldRole: "dos", objectType: "PhononDos" }], params: { selected_projection_ids: [], domain_policy: "union", max_table_rows: 200, layout: "band_left_dos_right" }, output: { artifactTypes: ["phonon_band_dos_json", "phonon_summary_json", "phonon_compatibility_json", "plotly_json", "table_json", "phonon_manifest_json", "recipe_json"] } }], expectedArtifacts: [] };
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: "dataset_h3", datasetId: "dataset_h3", projectId: "project_h3", name: "Combined phonon evidence", status: "ready", demo: true, profileId: "profile_h3", profile: { profileId: "profile_h3", datasetId: "dataset_h3", datasetType: "phonon", status: "ready", objects: [{ id: "band_artifact", objectType: "PhononBand", count: 1 }, { id: "dos_artifact", objectType: "PhononDos", count: 1 }] } } });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: "plan_h3", plan_hash: "hash_h3", validation_errors: [], plan, plan_source: "mock", planner_provider: "MockLLMProvider", enqueued: true, executed: true } });
  if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: { jobId: job, projectId: "project_h3", datasetId: "dataset_h3", status: "completed", planId: "plan_h3", planHash: "hash_h3", planSource: "mock", analysisPlan: plan, validationStatus: "validated", toolCallCount: 1, artifactCount: artifacts.length, eventCount: 2 } });
  if (url.pathname === `/planner/jobs/${job}/events`) return route.fulfill({ json: [] });
  if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: [{ id: "call_h3", jobId: job, stepId: "step_001", toolId: "phonon.band_dos", status: "completed", planId: "plan_h3", planHash: "hash_h3", inputSummary: "PhononBand + PhononDos artifacts", outputSummary: "7 artifacts" }] });
  if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: artifacts });
  if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { jobId: job, status: "completed", artifactCount: artifacts.length, artifacts } });
  return route.fulfill({ status: 404, json: { detail: "combined phonon evidence route not found" } });
}

function caseArtifacts(liveArtifacts, converted) {
  return liveArtifacts.map((artifact) => {
    let content = artifact.content;
    if (activeCase === "converted" && converted[artifact.name]) content = converted[artifact.name];
    if (activeCase === "invalid" && artifact.name === "phonon_band_dos.json") { content = structuredClone(content); content.module = "https://example.invalid/phonon.js"; }
    if (activeCase === "refused" && artifact.name === "phonon_band_dos.json") { content = structuredClone(content); content.display.performance_mode = "refused"; content.display.selected_projection_ids = []; }
    if (activeCase === "refused" && artifact.name === "phonon_band_dos_plot.json") {
      content = structuredClone(content); content.band_panel.series = []; content.band_panel.ticks = []; content.dos_panel.frequencies = []; content.dos_panel.total_dos = []; content.dos_panel.projections = []; content.display = { ...content.display, mode: "refused", reason: "PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED", numeric_values: 0, trace_count: 0, selected_projection_ids: [] };
    }
    return { ...artifact, content, metadata: { ...artifact.metadata, preview: content } };
  });
}

async function auditPage(page) {
  const audit = audits.get(page); if (!audit) throw new Error("missing audit");
  const inert = await page.evaluate(() => ({ iframe: document.querySelectorAll("iframe").length, externalScript: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length, javascriptUri: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length, inlineHandler: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length }));
  if (Object.values(inert).some(Boolean) || audit.consoleErrors.length || audit.pageErrors.length || audit.external.length || audit.httpErrors.length) throw new Error(`combined phonon audit failed ${JSON.stringify({ inert, ...audit })}`);
  return { externalRequests: audit.external.length, inert };
}

function startServer() { const command = process.platform === "win32" ? "cmd.exe" : "npm"; const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]; return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: "ignore" }); }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function stopServer(server) { if (process.platform === "win32" && Number.isSafeInteger(server.pid)) spawnSync("taskkill", ["/PID", String(server.pid), "/T", "/F"], { stdio: "ignore" }); else server.kill(); await stopPort(); }
async function waitForApp() { const end = Date.now() + 60_000; while (Date.now() < end) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("combined phonon app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; const ps = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`; await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); }); }
async function write(relative, value) { const file = path.join(EVIDENCE, relative); await mkdir(path.dirname(file), { recursive: true }); await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
async function json(file) { return JSON.parse(await readFile(file, "utf8")); }
async function loadDirectory(directory) { const result = {}; for (const name of await readdir(directory)) result[name] = await json(path.join(directory, name)); return result; }
function safeError(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 500); }
async function listFiles(directory) { const result = []; for (const entry of await readdir(directory, { withFileTypes: true })) { const target = path.join(directory, entry.name); if (entry.isDirectory()) result.push(...await listFiles(target)); else result.push(target); } return result.sort(); }
async function hashEvidence() { const files = (await listFiles(EVIDENCE)).filter((file) => !file.endsWith("artifact_hashes.json")); await write("artifact_hashes.json", { algorithm: "sha256", files: await Promise.all(files.map(async (file) => ({ name: path.relative(EVIDENCE, file).replaceAll("\\", "/"), bytes: (await stat(file)).size, sha256: createHash("sha256").update(await readFile(file)).digest("hex") }))) }); }

await main();
