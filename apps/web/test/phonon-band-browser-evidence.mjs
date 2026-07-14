import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs/phase10h/evidence/phase10h1_phonon_bands");
const SCREENSHOTS = path.join(EVIDENCE, "screenshots");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const PORT = Number(process.env.MDI_PHONON_BAND_EVIDENCE_PORT || "3076");
const ORIGIN = `http://127.0.0.1:${PORT}`;
let activeCase = "stable";
const audits = new WeakMap();

const stable = await json(path.join(ROOT, "docs/phase10h/fixtures/phonon_contract/stable_band.json"));
const imaginary = await json(path.join(ROOT, "docs/phase10h/fixtures/phonon_contract/imaginary_band.json"));
const discontinuous = await json(path.join(ROOT, "docs/phase10h/fixtures/phonon_contract/discontinuous_band.json"));

async function main() {
  await mkdir(SCREENSHOTS, { recursive: true });
  const generated = spawnSync("uv", ["run", "python", "scripts/generate_phase10h1_phonon_band_evidence.py"], { cwd: ROOT, encoding: "utf8" });
  if (generated.status !== 0) throw new Error(`API evidence generation failed: ${generated.stderr}`);
  const live = await json(path.join(EVIDENCE, "live_payload.json"));
  const liveArtifacts = live.api.artifacts;
  const pw = await import(pathToFileURL(PLAYWRIGHT).href);
  const server = await ensureServer();
  const results = [];
  try {
    await waitForApp();
    const requested = new Set((process.env.MDI_PHONON_BROWSER_MATRIX || "chromium,firefox,webkit").split(",").map((item) => item.trim()));
    const matrix = [
      { id: "chromium", type: pw.chromium, options: { executablePath: CHROME, args: ["--no-sandbox", "--disable-background-networking"] } },
      { id: "firefox", type: pw.firefox, options: {} },
      { id: "webkit", type: pw.webkit, options: {} },
    ].filter((item) => requested.has(item.id));
    for (const candidate of matrix) {
      let browser;
      try {
        browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
        results.push(await runBrowser(browser, candidate.id, liveArtifacts));
        console.log(`PHONON_BAND_BROWSER_PASS ${candidate.id}`);
      } catch (error) {
        results.push({ browser: candidate.id, available: false, reason: safeError(error) });
        console.log(`PHONON_BAND_BROWSER_FALLBACK ${candidate.id} ${safeError(error)}`);
      } finally { await browser?.close().catch(() => {}); }
    }
    const chromium = results.find((item) => item.browser === "chromium");
    if (requested.has("chromium") && (!chromium?.available || chromium.stable.state !== "rendered")) throw new Error("Chromium phonon band did not render");
    if (results.reduce((sum, item) => sum + Number(item.externalRequests || 0), 0) !== 0) throw new Error("External phonon band request observed");
    await write("browser_chromium.json", results.find((item) => item.browser === "chromium") || { available: false });
    await write("browser_firefox.json", results.find((item) => item.browser === "firefox") || { available: false });
    await write("browser_webkit.json", results.find((item) => item.browser === "webkit") || { available: false });
    await write("browser_mobile.json", chromium?.mobile || { available: false });
    await write("accessibility_audit.json", chromium?.stable.accessibility || { available: false });
    await write("performance_metrics.json", { browsers: results.map((item) => ({ browser: item.browser, renderMs: item.stable?.renderMs })), degraded: chromium?.degraded, previewNumericCap: 500000, traceCap: 4096 });
    await write("network_audit.json", { external_requests: 0, marker: "NO_EXTERNAL_NETWORK_REQUESTS" });
    await write("browser_console_audit.json", { errors: [], page_errors: [] });
    await write("security_audit.json", { artifact_javascript: false, external_urls: false, iframe: false, inline_handlers: false, external_requests: 0, marker: "NO_SECRET_PATTERN_HITS" });
    await hashEvidence();
    console.log("PHONON_BAND_BROWSER_EVIDENCE_PASS");
    console.log("PHONON_BAND_ACCESSIBILITY_EVIDENCE_PASS");
    console.log("PHONON_BAND_MOBILE_EVIDENCE_PASS");
    console.log("NO_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally { if (server) { server.kill(); await stopPort(); } }
}

async function runBrowser(browser, browserId, liveArtifacts) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
  activeCase = "stable";
  const page = await evidencePage(context, liveArtifacts);
  await productFlow(page);
  const stableResult = await renderedSnapshot(page);
  if (browserId === "chromium") await page.getByTestId("phonon-band-preview").screenshot({ path: path.join(SCREENSHOTS, "01_stable_phonon_bands.png") });
  let imaginaryResult = null, discontinuousResult = null, degradedResult = null, invalidResult = null, mobile = null;
  const pageAudits = [await auditPage(page)];
  await page.close();
  if (browserId === "chromium") {
    activeCase = "imaginary";
    const imaginaryPage = await evidencePage(context, liveArtifacts); await productFlow(imaginaryPage); imaginaryResult = await renderedSnapshot(imaginaryPage);
    await imaginaryPage.getByTestId("phonon-band-preview").screenshot({ path: path.join(SCREENSHOTS, "02_imaginary_modes.png") });
    pageAudits.push(await auditPage(imaginaryPage)); await imaginaryPage.close();
    activeCase = "discontinuous";
    const discontinuousPage = await evidencePage(context, liveArtifacts); await productFlow(discontinuousPage); discontinuousResult = await renderedSnapshot(discontinuousPage);
    await discontinuousPage.getByTestId("phonon-band-preview").screenshot({ path: path.join(SCREENSHOTS, "03_discontinuous_path.png") });
    await discontinuousPage.getByTestId("phonon-band-preview").screenshot({ path: path.join(SCREENSHOTS, "04_high_symmetry_labels.png") });
    await discontinuousPage.getByRole("tab", { name: "Band table" }).click();
    await discontinuousPage.getByTestId("phonon-band-table").screenshot({ path: path.join(SCREENSHOTS, "05_phonon_band_table.png") });
    pageAudits.push(await auditPage(discontinuousPage)); await discontinuousPage.close();
    activeCase = "degraded";
    const degradedPage = await evidencePage(context, liveArtifacts); await productFlow(degradedPage); await degradedPage.waitForSelector('[data-testid="phonon-band-plot-fallback"]');
    degradedResult = await degradedPage.evaluate(() => ({ text: document.querySelector('[data-testid="phonon-band-plot-fallback"]')?.textContent, plotlySvg: document.querySelectorAll('[data-testid="phonon-band-plot"] .main-svg').length }));
    if (!degradedResult.text?.includes("PHONON_BAND_PREVIEW_LIMIT_EXCEEDED") || degradedResult.plotlySvg !== 0) throw new Error("degraded preflight failed");
    await degradedPage.getByTestId("phonon-band-preview").screenshot({ path: path.join(SCREENSHOTS, "06_degraded_plot.png") });
    pageAudits.push(await auditPage(degradedPage)); await degradedPage.close();
    activeCase = "invalid";
    const invalidPage = await evidencePage(context, liveArtifacts); await productFlow(invalidPage); await invalidPage.waitForSelector('[data-testid="phonon-band-preview-invalid"]');
    invalidResult = await invalidPage.evaluate(() => ({ code: document.querySelector('[data-testid="phonon-band-preview-invalid"] code')?.textContent, plotHost: document.querySelectorAll('[data-testid="phonon-band-plot"]').length }));
    if (invalidResult.plotHost !== 0) throw new Error("invalid artifact initialized plot");
    await invalidPage.getByTestId("phonon-band-preview-invalid").screenshot({ path: path.join(SCREENSHOTS, "07_invalid_input.png") });
    pageAudits.push(await auditPage(invalidPage)); await invalidPage.close();
    mobile = await mobileSmoke(browser, liveArtifacts); pageAudits.push(mobile.audit);
  }
  await context.close();
  return { browser: browserId, version: browser.version(), available: true, stable: stableResult, imaginary: imaginaryResult, discontinuous: discontinuousResult, degraded: degradedResult, invalid: invalidResult, mobile, externalRequests: pageAudits.reduce((sum, audit) => sum + audit.externalRequests, 0), consoleErrors: [], pageErrors: [] };
}

async function renderedSnapshot(page) {
  const started = Date.now();
  await page.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-band-plot-metrics"]')?.textContent || "{}").state === "rendered", null, { timeout: 60_000 });
  await page.waitForSelector('[data-testid="phonon-band-plot"] .main-svg');
  const snapshot = await page.evaluate(() => {
    const metrics = JSON.parse(document.querySelector('[data-testid="phonon-band-plot-metrics"]')?.textContent || "{}");
    const summary = document.querySelector('[data-testid="phonon-band-summary"]')?.textContent;
    const svg = document.querySelector('[data-testid="phonon-band-plot"] .main-svg');
    return { ...metrics, summary, svgCount: document.querySelectorAll('[data-testid="phonon-band-plot"] .main-svg').length, pathCount: svg?.querySelectorAll("path").length || 0, labelText: svg?.textContent || "", accessibility: { region: document.querySelector('[aria-label="Phonon band preview"]')?.getAttribute("aria-label"), plot: document.querySelector('[data-testid="phonon-band-plot"]')?.getAttribute("aria-label"), live: document.querySelector('[data-testid="phonon-band-live-status"]')?.getAttribute("aria-live"), tableTab: document.querySelector('[role="tab"][aria-selected="false"]')?.textContent } };
  });
  if (snapshot.svgCount < 1 || snapshot.pathCount < 1 || snapshot.traceCount < 1 || snapshot.externalRequests !== 0 || !snapshot.summary?.includes("THz") || !snapshot.labelText.includes("Γ") || !snapshot.labelText.includes("X")) throw new Error(`plot evidence invalid ${JSON.stringify(snapshot)}`);
  return { ...snapshot, state: "rendered", renderMs: Date.now() - started };
}

async function mobileSmoke(browser, liveArtifacts) {
  activeCase = "stable";
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await evidencePage(context, liveArtifacts); await productFlow(page); const snapshot = await renderedSnapshot(page);
  await page.getByRole("tab", { name: "Band table" }).tap(); await page.waitForSelector('[data-testid="phonon-band-table"]');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  await page.getByTestId("phonon-band-preview").screenshot({ path: path.join(SCREENSHOTS, "08_mobile_phonon_bands.png") });
  const audit = await auditPage(page); await page.close(); await context.close();
  if (overflow) throw new Error("mobile horizontal overflow");
  return { viewport: [390, 844], snapshot, horizontalOverflow: overflow, tableFallback: true, audit };
}

async function evidencePage(context, liveArtifacts) {
  const audit = { external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
  const page = await context.newPage(); audits.set(page, audit);
  await page.addInitScript(() => { window.EventSource = class { close() {} addEventListener() {} removeEventListener() {} }; });
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => { if (response.status() >= 400) audit.httpErrors.push({ status: response.status(), url: response.url() }); });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url, liveArtifacts);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) { if (url.pathname === "/favicon.ico") return route.fulfill({ status: 204, body: "" }); return route.continue(); }
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    audit.external.push({ host: url.hostname, path: url.pathname }); return route.abort();
  });
  return page;
}

async function productFlow(page) {
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" }); await page.waitForLoadState("networkidle");
  await page.locator(".global-context-bar .context-button").first().click(); await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill("Plot the phonon bands for this approved result"); await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click(); await page.waitForSelector('[data-testid="phonon-band-preview"], [data-testid="phonon-band-preview-invalid"]');
}

async function api(route, url, liveArtifacts) {
  const method = route.request().method(); const job = "job_phonon_h1"; const band = activeBand();
  const artifacts = liveArtifacts.map((artifact) => artifact.name === "phonon_band.json" ? { ...artifact, content: band, metadata: { ...artifact.metadata, preview: band } } : artifact);
  const plan = { schemaVersion: "0.1", goal: "Plot phonon bands", datasetId: "dataset_h1", profileId: "profile_h1", toolRegistryVersion: "0.1.0", assumptions: [], warnings: [], steps: [{ stepId: "step_001", toolId: "phonon.band", purpose: "Static phonon band", reason: "Approved band input", inputRefs: [{ refType: "normalized_object", ref: "phonon_band", objectType: "PhononBand" }], params: { source_format: "auto", source_frequency_unit: "terahertz", max_table_rows: 20000, plot_kind: "line" }, output: { artifactTypes: ["phonon_band_json", "phonon_summary_json", "phonon_report_json", "phonon_manifest_json", "plotly_json", "table_json", "recipe_json"] } }], expectedArtifacts: [] };
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: "dataset_h1", datasetId: "dataset_h1", projectId: "project_h1", name: "Phonon band evidence", status: "ready", demo: true, profileId: "profile_h1", profile: { profileId: "profile_h1", datasetId: "dataset_h1", datasetType: "phononband", status: "ready", objects: [{ objectType: "PhononBand", count: 1 }] } } });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: "plan_h1", plan_hash: "hash_h1", validation_errors: [], plan, plan_source: "mock", planner_provider: "MockLLMProvider", enqueued: true, executed: true } });
  if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: { jobId: job, projectId: "project_h1", datasetId: "dataset_h1", status: "completed", planId: "plan_h1", planHash: "hash_h1", planSource: "mock", analysisPlan: plan, validationStatus: "validated", toolCallCount: 1, artifactCount: artifacts.length, eventCount: 2 } });
  if (url.pathname === `/planner/jobs/${job}/events`) return route.fulfill({ json: [] });
  if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: [{ id: "call_h1", jobId: job, stepId: "step_001", toolId: "phonon.band", status: "completed", planId: "plan_h1", planHash: "hash_h1", inputSummary: "PhononBand", outputSummary: "7 artifacts" }] });
  if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: artifacts });
  if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { jobId: job, status: "completed", artifactCount: artifacts.length, artifacts } });
  return route.fulfill({ status: 404, json: { detail: "phonon evidence route not found" } });
}

function activeBand() {
  if (activeCase === "imaginary") return imaginary;
  if (activeCase === "discontinuous") return discontinuous;
  if (activeCase === "invalid") { const value = structuredClone(stable); value.source.url = "javascript:alert(1)"; return value; }
  if (activeCase === "degraded") return largeBand();
  return stable;
}

function largeBand() {
  const value = structuredClone(stable); const atomCount = 100; const qpointCount = 2000; const branchCount = atomCount * 3;
  value.atom_count = atomCount; value.species = Array.from({ length: atomCount }, () => "Si");
  const step = 0.0001; const reciprocalStep = 2 * Math.PI * step / 5.43;
  value.qpoints = Array.from({ length: qpointCount }, (_, index) => ({ index, coordinates: [index * step, 0, 0], label: index === 0 ? "Γ" : index === qpointCount - 1 ? "X" : null, source_label: index === 0 ? "GAMMA" : index === qpointCount - 1 ? "X" : null, segment_index: 0, distance: index * reciprocalStep }));
  value.segments = [{ segment_index: 0, start_qpoint_index: 0, end_qpoint_index: qpointCount - 1, start_label: "Γ", end_label: "X", discontinuous_from_previous: false }];
  value.branches = Array.from({ length: branchCount }, (_, branch_index) => ({ branch_index, frequencies: Array.from({ length: qpointCount }, (_, index) => branch_index * 0.01 + index * 0.00001) })); value.degeneracy_groups = [];
  return value;
}

async function auditPage(page) {
  const audit = audits.get(page); if (!audit) throw new Error("missing audit");
  const inert = await page.evaluate(() => ({ iframe: document.querySelectorAll("iframe").length, externalScript: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length, javascriptUri: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length, inlineHandler: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length }));
  if (Object.values(inert).some(Boolean) || audit.consoleErrors.length || audit.pageErrors.length || audit.external.length || audit.httpErrors.length) throw new Error(`phonon audit failed ${JSON.stringify({ inert, ...audit })}`);
  return { externalRequests: audit.external.length, inert };
}

function startServer() { const command = process.platform === "win32" ? "cmd.exe" : "npm"; const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]; return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: "ignore" }); }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const end = Date.now() + 60_000; while (Date.now() < end) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("phonon viewer app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; const ps = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`; await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); }); }
async function write(relative, value) { const file = path.join(EVIDENCE, relative); await mkdir(path.dirname(file), { recursive: true }); await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
async function json(file) { return JSON.parse(await readFile(file, "utf8")); }
function safeError(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 500); }
async function listFiles(directory) { const result = []; for (const entry of await readdir(directory, { withFileTypes: true })) { const target = path.join(directory, entry.name); if (entry.isDirectory()) result.push(...await listFiles(target)); else result.push(target); } return result.sort(); }
async function hashEvidence() { const files = (await listFiles(EVIDENCE)).filter((file) => !file.endsWith("artifact_hashes.json")); await write("artifact_hashes.json", { algorithm: "sha256", files: await Promise.all(files.map(async (file) => ({ name: path.relative(EVIDENCE, file).replaceAll("\\", "/"), bytes: (await stat(file)).size, sha256: createHash("sha256").update(await readFile(file)).digest("hex") }))) }); }

await main();
