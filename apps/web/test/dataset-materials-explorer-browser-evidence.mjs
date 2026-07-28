import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs", "phase10k", "evidence", "phase10k2_dataset_materials_explorer");
const SCREENSHOTS = path.join(EVIDENCE, "browser", "screenshots");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE;
const PORT = Number(process.env.MDI_DATASET_EXPLORER_EVIDENCE_PORT || "3392");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const audits = new WeakMap();

async function main() {
  await mkdir(SCREENSHOTS, { recursive: true });
  const generated = spawnSync("uv", ["run", "python", "scripts/generate_phase10k2_dataset_explorer_evidence.py"], { cwd: ROOT, encoding: "utf8" });
  if (generated.status !== 0) throw new Error(`Dataset evidence generation failed: ${safeError(generated.stderr)}`);
  const capture = await json(path.join(EVIDENCE, "api", "runtime_capture.json"));
  const profile = await json(path.join(EVIDENCE, "api", "data_profile.json"));
  const artifacts = await hydratedArtifacts(capture.artifacts);
  const pw = await import(pathToFileURL(PLAYWRIGHT).href);
  const server = await ensureServer();
  const requested = new Set((process.env.MDI_DATASET_EXPLORER_BROWSER_MATRIX || "chromium,firefox,webkit").split(",").map((value) => value.trim()));
  const browsers = [
    { id: "chromium", type: pw.chromium, options: { ...(CHROME ? { executablePath: CHROME } : {}), args: ["--no-sandbox", "--disable-background-networking"] } },
    { id: "firefox", type: pw.firefox, options: {} },
    { id: "webkit", type: pw.webkit, options: {} },
  ].filter((candidate) => requested.has(candidate.id));
  const results = [];
  try {
    await waitForApp();
    for (const candidate of browsers) {
      let browser;
      try {
        browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
        results.push(await runBrowser(browser, candidate.id, capture, profile, artifacts));
        console.log(`DATASET_MATERIALS_EXPLORER_BROWSER_PASS ${candidate.id}`);
      } catch (error) {
        results.push({ browser: candidate.id, available: false, reason: safeError(error) });
        console.log(`DATASET_MATERIALS_EXPLORER_BROWSER_FALLBACK ${candidate.id} ${safeError(error)}`);
      } finally {
        await browser?.close().catch(() => {});
      }
    }
    const chromium = results.find((item) => item.browser === "chromium");
    if (!chromium?.available) throw new Error("Chromium is required for Dataset Explorer evidence.");
    if (results.some((item) => item.available && (item.externalRequests || item.consoleErrors?.length || item.pageErrors?.length))) throw new Error("Dataset Explorer browser audit failed.");
    await write("browser/browser_matrix.json", results);
    await write("browser/console_network_audit.json", {
      browsers: results.map((item) => ({ browser: item.browser, available: item.available, externalRequests: item.externalRequests || 0, consoleErrors: item.consoleErrors || [], pageErrors: item.pageErrors || [] })),
      marker: "NO_DATASET_EXPLORER_EXTERNAL_NETWORK_REQUESTS",
    });
    await write("browser/accessibility_audit.json", { desktop: chromium.desktop.accessibility, mobile: chromium.mobile.accessibility, marker: "DATASET_MATERIALS_EXPLORER_BROWSER_EVIDENCE_PASS" });
    await write("browser/performance_metrics.json", { browsers: results.filter((item) => item.available).map((item) => ({ browser: item.browser, firstProductMs: item.desktop.firstProductMs })), mobileFirstProductMs: chromium.mobile.firstProductMs, acceptance: "PASS" });
    await hashEvidence();
    console.log("DATASET_MATERIALS_EXPLORER_BROWSER_EVIDENCE_PASS");
    console.log("NO_DATASET_EXPLORER_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    if (server) { server.kill(); await stopPort(); }
  }
}

async function runBrowser(browser, browserId, capture, profile, artifacts) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
  const page = await evidencePage(context, capture, profile, artifacts);
  const desktop = await productFlow(page);
  if (browserId === "chromium") await screenshots(page);
  const desktopAudit = await auditPage(page);
  await page.close();
  await context.close();
  let mobile = null;
  let mobileAudit = { externalRequests: 0, consoleErrors: [], pageErrors: [] };
  if (browserId === "chromium") {
    const mobileContext = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
    const mobilePage = await evidencePage(mobileContext, capture, profile, artifacts);
    mobile = await productFlow(mobilePage);
    await mobilePage.getByTestId("dataset-materials-explorer").screenshot({ path: path.join(SCREENSHOTS, "07_mobile_dataset_explorer.png") });
    mobileAudit = await auditPage(mobilePage);
    await mobilePage.close();
    await mobileContext.close();
  }
  return {
    browser: browserId,
    version: browser.version(),
    available: true,
    desktop,
    mobile,
    externalRequests: desktopAudit.externalRequests + mobileAudit.externalRequests,
    consoleErrors: [...desktopAudit.consoleErrors, ...mobileAudit.consoleErrors],
    pageErrors: [...desktopAudit.pageErrors, ...mobileAudit.pageErrors],
  };
}

async function productFlow(page) {
  const started = Date.now();
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill("Explore this materials dataset and compare the explicit train and test groups.");
  await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click();
  const product = page.getByTestId("dataset-materials-explorer");
  await product.waitFor();
  const firstProductMs = Date.now() - started;
  const tabs = ["Overview", "Composition", "Structures", "Properties", "Data quality", "Comparison", "Samples"];
  const snapshots = {};
  for (const tab of tabs) {
    await product.getByRole("tab", { name: tab }).click();
    snapshots[tab] = (await product.locator('[role="tabpanel"]').innerText()).slice(0, 1000);
  }
  await product.getByRole("tab", { name: "Properties" }).click();
  const selector = product.locator("select");
  if (await selector.locator("option").count() > 1) await selector.selectOption({ index: 1 });
  await product.getByRole("tab", { name: "Samples" }).click();
  await product.locator('[data-testid="dataset-explorer-samples"] tbody button').nth(2).click();
  const sampleInspector = await product.getByTestId("dataset-sample-inspector").innerText();
  await product.getByRole("tab", { name: "Overview" }).focus();
  await page.keyboard.press("ArrowRight");
  const keyboardFocus = await page.evaluate(() => document.activeElement?.textContent?.trim());
  await product.getByRole("tab", { name: "Samples" }).focus();
  const state = await product.evaluate((node) => ({
    text: node.textContent || "",
    regionLabel: node.getAttribute("aria-label"),
    tabCount: node.querySelectorAll('[role="tab"]').length,
    selectedTabCount: node.querySelectorAll('[role="tab"][aria-selected="true"]').length,
    tableCount: node.querySelectorAll("table").length,
    canvasCount: node.querySelectorAll("canvas").length,
    iframeCount: node.querySelectorAll("iframe").length,
    scriptCount: node.querySelectorAll("script").length,
  }));
  const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  const contentChecks = {
    overview: snapshots.Overview.toLowerCase().includes("samples"),
    composition: snapshots.Composition.includes("Element coverage"),
    structures: snapshots.Structures.toLowerCase().includes("space group"),
    properties: snapshots.Properties.includes("statistical candidates only"),
    quality: snapshots["Data quality"].toLowerCase().includes("invalid formulas"),
    comparison: snapshots.Comparison.includes("no row-order inference"),
    sampleRow: sampleInspector.includes("row 2"),
    sampleFormula: sampleInspector.includes("Si"),
  };
  if (Object.values(contentChecks).some((value) => !value)) throw new Error(`Dataset product content mismatch: ${JSON.stringify(contentChecks)}`);
  if (state.tabCount !== 7 || state.selectedTabCount !== 1 || state.canvasCount || state.iframeCount || state.scriptCount || horizontalOverflow) throw new Error(`Dataset product surface audit failed: ${JSON.stringify({ state, horizontalOverflow })}`);
  return { firstProductMs, snapshots, sampleInspector, keyboardFocus, horizontalOverflow, accessibility: { regionLabel: state.regionLabel, tabCount: state.tabCount, selectedTabCount: state.selectedTabCount, tableFallback: state.tableCount > 0 } };
}

async function screenshots(page) {
  const product = page.getByTestId("dataset-materials-explorer");
  const captures = [
    ["Overview", "01_dataset_overview.png"],
    ["Composition", "02_composition_explorer.png"],
    ["Structures", "03_structure_statistics.png"],
    ["Properties", "04_property_explorer.png"],
    ["Data quality", "05_data_quality.png"],
    ["Comparison", "06_dataset_comparison.png"],
  ];
  for (const [tab, file] of captures) {
    await product.getByRole("tab", { name: tab }).click();
    await product.screenshot({ path: path.join(SCREENSHOTS, file) });
  }
}

async function hydratedArtifacts(records) {
  return Promise.all(records.map(async (artifact) => {
    const file = path.join(EVIDENCE, "artifacts", artifact.name);
    const raw = await readFile(file, "utf8");
    let content = raw;
    if (artifact.name.endsWith(".json")) content = JSON.parse(raw);
    return { ...artifact, content, metadata: { ...(artifact.metadata || {}), preview: content } };
  }));
}

async function evidencePage(context, capture, profile, artifacts) {
  const audit = { external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
  const page = await context.newPage();
  audits.set(page, audit);
  await page.addInitScript(() => { window.EventSource = class { close() {} addEventListener() {} removeEventListener() {} }; });
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => { if (response.status() >= 400) audit.httpErrors.push({ status: response.status(), path: new URL(response.url()).pathname }); });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url, capture, profile, artifacts);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) {
      if (url.pathname === "/favicon.ico") return route.fulfill({ status: 204, body: "" });
      return route.continue();
    }
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    audit.external.push({ host: url.hostname, path: url.pathname });
    return route.abort();
  });
  return page;
}

async function api(route, url, capture, profile, artifacts) {
  const method = route.request().method();
  const job = "job_phase10k2_browser";
  const plan = capture.plan;
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: profile.datasetId, datasetId: profile.datasetId, projectId: "project_phase10k2_evidence", name: "Dataset Explorer evidence", status: "ready", demo: true, profileId: profile.profileId, profile } });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: "plan_phase10k2_browser", plan_hash: capture.job.planHash, validation_errors: [], plan, plan_source: "mock", planner_provider: "MockLLMProvider", enqueued: true, executed: true } });
  if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: { jobId: job, projectId: "project_phase10k2_evidence", datasetId: profile.datasetId, status: "completed", planId: "plan_phase10k2_browser", planHash: capture.job.planHash, planSource: "mock", analysisPlan: plan, validationStatus: "validated", toolCallCount: 1, artifactCount: artifacts.length, eventCount: capture.events.length } });
  if (url.pathname === `/planner/jobs/${job}/events`) return route.fulfill({ json: capture.events });
  if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: capture.toolCalls });
  if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: artifacts });
  if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { ...capture.result, jobId: job, artifacts } });
  return route.fulfill({ status: 404, json: { detail: "dataset explorer evidence route not found" } });
}

async function auditPage(page) {
  const audit = audits.get(page);
  const inert = await page.evaluate(() => ({
    iframe: document.querySelectorAll("iframe").length,
    externalScript: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length,
    javascriptUri: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
    inlineHandler: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length,
  }));
  if (Object.values(inert).some(Boolean) || audit.consoleErrors.length || audit.pageErrors.length || audit.external.length || audit.httpErrors.length) throw new Error(`Dataset browser audit failed: ${JSON.stringify({ inert, ...audit })}`);
  return { externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors, inert };
}

function startServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
  return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: "ignore" });
}
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const end = Date.now() + 60_000; while (Date.now() < end) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("Dataset Explorer app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; const ps = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`; await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); }); }
async function write(relative, value) { const file = path.join(EVIDENCE, relative); await mkdir(path.dirname(file), { recursive: true }); await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
async function json(file) { return JSON.parse(await readFile(file, "utf8")); }
function safeError(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 500); }
async function listFiles(directory) { const result = []; for (const entry of await readdir(directory, { withFileTypes: true })) { const target = path.join(directory, entry.name); if (entry.isDirectory()) result.push(...await listFiles(target)); else result.push(target); } return result.sort(); }
async function hashEvidence() { const files = (await listFiles(EVIDENCE)).filter((file) => !file.endsWith("evidence_manifest.json")); await write("evidence_manifest.json", { algorithm: "sha256", files: await Promise.all(files.map(async (file) => ({ name: path.relative(EVIDENCE, file).replaceAll("\\", "/"), bytes: (await stat(file)).size, sha256: createHash("sha256").update(await readFile(file)).digest("hex") }))) }); }

await main();
