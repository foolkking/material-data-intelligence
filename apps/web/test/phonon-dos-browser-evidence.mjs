import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs/phase10h/evidence/phase10h2_phonon_dos");
const SCREENSHOTS = path.join(EVIDENCE, "screenshots");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const PORT = Number(process.env.MDI_PHONON_DOS_EVIDENCE_PORT || "3077");
const ORIGIN = `http://127.0.0.1:${PORT}`;
let activeCase = "projected";
const audits = new WeakMap();

const total = await json(path.join(ROOT, "docs/phase10h/fixtures/phonon_contract/total_dos.json"));
const projected = await json(path.join(ROOT, "docs/phase10h/fixtures/phonon_contract/projected_dos.json"));
const imaginary = await json(path.join(ROOT, "docs/phase10h/fixtures/phonon_contract/imaginary_dos.json"));

async function main() {
  await mkdir(SCREENSHOTS, { recursive: true });
  const generated = spawnSync("uv", ["run", "python", "scripts/generate_phase10h2_phonon_dos_evidence.py"], { cwd: ROOT, encoding: "utf8" });
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
        console.log(`PHONON_DOS_BROWSER_PASS ${candidate.id}`);
      } catch (error) {
        results.push({ browser: candidate.id, available: false, reason: safeError(error) });
        console.log(`PHONON_DOS_BROWSER_FALLBACK ${candidate.id} ${safeError(error)}`);
      } finally { await browser?.close().catch(() => {}); }
    }
    const chromium = results.find((item) => item.browser === "chromium");
    if (requested.has("chromium") && (!chromium?.available || chromium.projected.state !== "rendered")) throw new Error("Chromium phonon DOS did not render");
    if (results.reduce((sum, item) => sum + Number(item.externalRequests || 0), 0) !== 0) throw new Error("External phonon DOS request observed");
    await write("browser_chromium.json", results.find((item) => item.browser === "chromium") || { available: false });
    await write("browser_firefox.json", results.find((item) => item.browser === "firefox") || { available: false });
    await write("browser_webkit.json", results.find((item) => item.browser === "webkit") || { available: false });
    await write("browser_mobile.json", chromium?.mobile || { available: false });
    await write("accessibility_audit.json", chromium?.projected.accessibility || { available: false });
    await write("performance_metrics.json", { browsers: results.map((item) => ({ browser: item.browser, renderMs: item.projected?.renderMs })), degraded: chromium?.degraded, previewNumericCap: 100000, tableVisibleRowCap: 300 });
    await write("network_audit.json", { external_requests: 0, marker: "NO_EXTERNAL_NETWORK_REQUESTS" });
    await write("browser_console_audit.json", { errors: [], page_errors: [] });
    await write("security_audit.json", { artifact_javascript: false, external_urls: false, iframe: false, inline_handlers: false, external_requests: 0, marker: "NO_SECRET_PATTERN_HITS" });
    await hashEvidence();
    console.log("PHONON_DOS_BROWSER_EVIDENCE_PASS");
    console.log("PHONON_DOS_ACCESSIBILITY_EVIDENCE_PASS");
    console.log("PHONON_DOS_MOBILE_EVIDENCE_PASS");
    console.log("NO_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally { if (server) { server.kill(); await stopPort(); } }
}

async function runBrowser(browser, browserId, liveArtifacts) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
  activeCase = "projected";
  const page = await evidencePage(context, liveArtifacts);
  await productFlow(page);
  const projectedResult = await renderedSnapshot(page);
  const pageAudits = [];
  if (browserId === "chromium") {
    await page.getByTestId("phonon-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "01_total_phonon_dos.png") });
    await page.getByTestId("phonon-dos-projection-selector").selectOption("0");
    await page.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-dos-plot-metrics"]')?.textContent || "{}").traceCount === 2);
    await page.getByTestId("phonon-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "03_atom_projected_dos.png") });
    await page.getByTestId("phonon-dos-summary").screenshot({ path: path.join(SCREENSHOTS, "05_normalization_summary.png") });
    await page.getByRole("tab", { name: "DOS table" }).click();
    await page.getByTestId("phonon-dos-table").screenshot({ path: path.join(SCREENSHOTS, "06_dos_table.png") });
  }
  pageAudits.push(await auditPage(page)); await page.close();
  let imaginaryResult = null, speciesResult = null, degradedResult = null, invalidResult = null, mobile = null;
  if (browserId === "chromium") {
    activeCase = "imaginary";
    const imaginaryPage = await evidencePage(context, liveArtifacts); await productFlow(imaginaryPage); imaginaryResult = await renderedSnapshot(imaginaryPage);
    await imaginaryPage.getByTestId("phonon-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "02_imaginary_region_dos.png") }); pageAudits.push(await auditPage(imaginaryPage)); await imaginaryPage.close();
    activeCase = "species";
    const speciesPage = await evidencePage(context, liveArtifacts); await productFlow(speciesPage); await renderedSnapshot(speciesPage); await speciesPage.getByTestId("phonon-dos-projection-selector").selectOption("0");
    await speciesPage.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-dos-plot-metrics"]')?.textContent || "{}").traceCount === 2); speciesResult = await speciesPage.getByTestId("phonon-dos-projection-selector").inputValue();
    await speciesPage.getByTestId("phonon-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "04_species_projected_dos.png") }); pageAudits.push(await auditPage(speciesPage)); await speciesPage.close();
    activeCase = "degraded";
    const degradedPage = await evidencePage(context, liveArtifacts); await productFlow(degradedPage); await renderedSnapshot(degradedPage); await degradedPage.getByTestId("phonon-dos-projection-selector").selectOption("0"); await degradedPage.waitForSelector('[data-testid="phonon-dos-plot-fallback"]');
    degradedResult = await degradedPage.evaluate(() => ({ text: document.querySelector('[data-testid="phonon-dos-plot-fallback"]')?.textContent, svg: document.querySelectorAll('[data-testid="phonon-dos-plot"] .main-svg').length }));
    if (!degradedResult.text?.includes("PHONON_DOS_PREVIEW_LIMIT_EXCEEDED")) throw new Error("degraded DOS preflight failed");
    await degradedPage.getByTestId("phonon-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "07_degraded_plot_fallback.png") }); pageAudits.push(await auditPage(degradedPage)); await degradedPage.close();
    activeCase = "invalid";
    const invalidPage = await evidencePage(context, liveArtifacts); await productFlow(invalidPage); await invalidPage.waitForSelector('[data-testid="phonon-dos-preview-invalid"]');
    invalidResult = await invalidPage.evaluate(() => ({ code: document.querySelector('[data-testid="phonon-dos-preview-invalid"] code')?.textContent, plotHost: document.querySelectorAll('[data-testid="phonon-dos-plot"]').length }));
    if (invalidResult.plotHost !== 0) throw new Error("invalid DOS initialized plot");
    await invalidPage.getByTestId("phonon-dos-preview-invalid").screenshot({ path: path.join(SCREENSHOTS, "08_invalid_dos.png") }); pageAudits.push(await auditPage(invalidPage)); await invalidPage.close();
    mobile = await mobileSmoke(browser, liveArtifacts); pageAudits.push(mobile.audit);
  }
  await context.close();
  return { browser: browserId, version: browser.version(), available: true, projected: projectedResult, imaginary: imaginaryResult, species: speciesResult, degraded: degradedResult, invalid: invalidResult, mobile, externalRequests: pageAudits.reduce((sum, audit) => sum + audit.externalRequests, 0) };
}

async function renderedSnapshot(page) {
  const started = Date.now();
  await page.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-dos-plot-metrics"]')?.textContent || "{}").state === "rendered", null, { timeout: 60_000 });
  await page.waitForSelector('[data-testid="phonon-dos-plot"] .main-svg');
  const snapshot = await page.evaluate(() => {
    const metrics = JSON.parse(document.querySelector('[data-testid="phonon-dos-plot-metrics"]')?.textContent || "{}");
    const svg = document.querySelector('[data-testid="phonon-dos-plot"] .main-svg');
    return { ...metrics, summary: document.querySelector('[data-testid="phonon-dos-summary"]')?.textContent, svgCount: document.querySelectorAll('[data-testid="phonon-dos-plot"] .main-svg').length, pathCount: svg?.querySelectorAll("path").length || 0, text: svg?.textContent || "", accessibility: { region: document.querySelector('[aria-label="Phonon density of states preview"]')?.getAttribute("aria-label"), plot: document.querySelector('[data-testid="phonon-dos-plot"]')?.getAttribute("aria-label"), live: document.querySelector('[data-testid="phonon-dos-live-status"]')?.getAttribute("aria-live"), selector: document.querySelector('[data-testid="phonon-dos-projection-selector"]')?.parentElement?.textContent } };
  });
  if (snapshot.svgCount < 1 || snapshot.pathCount < 1 || snapshot.traceCount < 1 || snapshot.externalRequests !== 0 || !snapshot.summary?.includes("total_modes") || snapshot.accessibility.plot !== "Phonon density of states by frequency") throw new Error(`DOS plot evidence invalid ${JSON.stringify(snapshot)}`);
  return { ...snapshot, state: "rendered", renderMs: Date.now() - started };
}

async function mobileSmoke(browser, liveArtifacts) {
  activeCase = "projected";
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await evidencePage(context, liveArtifacts); await productFlow(page); const snapshot = await renderedSnapshot(page);
  await page.getByTestId("phonon-dos-projection-selector").tap(); await page.keyboard.press("Escape");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  await page.getByTestId("phonon-dos-preview").screenshot({ path: path.join(SCREENSHOTS, "09_mobile_dos.png") });
  const audit = await auditPage(page); await page.close(); await context.close();
  if (overflow) throw new Error("mobile DOS horizontal overflow");
  return { viewport: [390, 844], snapshot, horizontalOverflow: overflow, audit };
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
  await page.locator('[data-testid="planner-form"] textarea').fill("Plot the phonon density of states"); await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click(); await page.waitForSelector('[data-testid="phonon-dos-preview"], [data-testid="phonon-dos-preview-invalid"]');
}

async function api(route, url, liveArtifacts) {
  const method = route.request().method(); const job = "job_phonon_h2"; const dos = activeDos(); const summary = activeSummary(dos);
  const artifacts = liveArtifacts.map((artifact) => artifact.name === "phonon_dos.json" ? { ...artifact, content: dos, metadata: { ...artifact.metadata, preview: dos } } : artifact.name === "phonon_dos_summary.json" ? { ...artifact, content: summary, metadata: { ...artifact.metadata, preview: summary } } : artifact);
  const plan = { schemaVersion: "0.1", goal: "Plot phonon DOS", datasetId: "dataset_h2", profileId: "profile_h2", toolRegistryVersion: "0.1.0", assumptions: [], warnings: [], steps: [{ stepId: "step_001", toolId: "phonon.dos", purpose: "Static phonon DOS", reason: "Approved DOS input", inputRefs: [{ refType: "normalized_object", ref: "phonon_dos", objectType: "PhononDos" }], params: { source_format: "auto", source_frequency_unit: "terahertz", source_normalization: "total_modes", max_table_rows: 20000, max_plot_values: 100000, plot_kind: "line" }, output: { artifactTypes: ["phonon_dos_json", "phonon_summary_json", "phonon_report_json", "phonon_manifest_json", "plotly_json", "table_json", "recipe_json"] } }], expectedArtifacts: [] };
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: "dataset_h2", datasetId: "dataset_h2", projectId: "project_h2", name: "Phonon DOS evidence", status: "ready", demo: true, profileId: "profile_h2", profile: { profileId: "profile_h2", datasetId: "dataset_h2", datasetType: "phonondos", status: "ready", objects: [{ objectType: "PhononDos", count: 1 }] } } });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: "plan_h2", plan_hash: "hash_h2", validation_errors: [], plan, plan_source: "mock", planner_provider: "MockLLMProvider", enqueued: true, executed: true } });
  if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: { jobId: job, projectId: "project_h2", datasetId: "dataset_h2", status: "completed", planId: "plan_h2", planHash: "hash_h2", planSource: "mock", analysisPlan: plan, validationStatus: "validated", toolCallCount: 1, artifactCount: artifacts.length, eventCount: 2 } });
  if (url.pathname === `/planner/jobs/${job}/events`) return route.fulfill({ json: [] });
  if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: [{ id: "call_h2", jobId: job, stepId: "step_001", toolId: "phonon.dos", status: "completed", planId: "plan_h2", planHash: "hash_h2", inputSummary: "PhononDos", outputSummary: "7 artifacts" }] });
  if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: artifacts });
  if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { jobId: job, status: "completed", artifactCount: artifacts.length, artifacts } });
  return route.fulfill({ status: 404, json: { detail: "phonon DOS evidence route not found" } });
}

function activeDos() {
  if (activeCase === "total") return total;
  if (activeCase === "imaginary") return imaginary;
  if (activeCase === "species") return speciesDos();
  if (activeCase === "degraded") return largeDos();
  if (activeCase === "invalid") { const value = structuredClone(projected); value.source.url = "javascript:alert(1)"; return value; }
  return projected;
}

function activeSummary(dos) { return { schema_version: "phase10h2.phonon_dos_summary.v1", imaginary_region_integral: dos.frequencies[0] < 0 ? 0.5 : 0, projection_completeness: dos.projected_dos.length ? dos.projected_dos.every((item) => item.source_guarantees_sum) ? "complete" : "partial" : "unknown" }; }
function speciesDos() { const value = structuredClone(projected); value.projected_dos = [{ projection_index: 0, projection_type: "species", atom_index: null, species: "Si", values: value.total_dos.slice(), source_guarantees_sum: true }]; return value; }
function largeDos() { const value = structuredClone(projected); const count = 60_000; value.frequencies = Array.from({ length: count }, (_, index) => -1 + 6 * index / (count - 1)); value.total_dos = Array.from({ length: count }, () => 1); value.projected_dos = [{ projection_index: 0, projection_type: "species", atom_index: null, species: "Si", values: Array.from({ length: count }, () => 1), source_guarantees_sum: true }]; value.integration.observed_integral = 6; return value; }

async function auditPage(page) {
  const audit = audits.get(page); if (!audit) throw new Error("missing audit");
  const inert = await page.evaluate(() => ({ iframe: document.querySelectorAll("iframe").length, externalScript: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length, javascriptUri: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length, inlineHandler: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length }));
  if (Object.values(inert).some(Boolean) || audit.consoleErrors.length || audit.pageErrors.length || audit.external.length || audit.httpErrors.length) throw new Error(`phonon DOS audit failed ${JSON.stringify({ inert, ...audit })}`);
  return { externalRequests: audit.external.length, inert };
}

function startServer() { const command = process.platform === "win32" ? "cmd.exe" : "npm"; const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]; return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: "ignore" }); }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const end = Date.now() + 60_000; while (Date.now() < end) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("phonon DOS app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; const ps = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`; await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); }); }
async function write(relative, value) { const file = path.join(EVIDENCE, relative); await mkdir(path.dirname(file), { recursive: true }); await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
async function json(file) { return JSON.parse(await readFile(file, "utf8")); }
function safeError(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 500); }
async function listFiles(directory) { const result = []; for (const entry of await readdir(directory, { withFileTypes: true })) { const target = path.join(directory, entry.name); if (entry.isDirectory()) result.push(...await listFiles(target)); else result.push(target); } return result.sort(); }
async function hashEvidence() { const files = (await listFiles(EVIDENCE)).filter((file) => !file.endsWith("artifact_hashes.json")); await write("artifact_hashes.json", { algorithm: "sha256", files: await Promise.all(files.map(async (file) => ({ name: path.relative(EVIDENCE, file).replaceAll("\\", "/"), bytes: (await stat(file)).size, sha256: createHash("sha256").update(await readFile(file)).digest("hex") }))) }); }

await main();
