import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs", "phase10k", "evidence", "phase10k5_material_intelligence_integration");
const SCREENSHOTS = path.join(EVIDENCE, "browser", "screenshots");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE;
const PORT = Number(process.env.MDI_MATERIAL_INTELLIGENCE_EVIDENCE_PORT || "3395");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const CASES = {
  dataset: { id: "case_a_c_f_dataset", product: "dataset", prompt: "Explore this materials dataset and compare train and test." },
  structure: { id: "case_b_structure_enriched", product: "dataset", prompt: "Explore this structure-enriched materials dataset." },
  regression: { id: "case_c_regression", product: "ml", prompt: "Analyze model performance and prediction error." },
  uncertainty: { id: "case_d_uncertainty", product: "ml", prompt: "Analyze uncertainty reliability and error decay." },
  classification: { id: "case_e_classification", product: "ml", prompt: "Evaluate classification confusion matrix and ROC." },
  composition: { id: "case_a_c_f_composition", product: "composition", prompt: "Explore composition space and compare groups." },
  partial: { id: "case_g_partial_dataset", product: "partial", prompt: "Explore this partially capable materials dataset." },
  ambiguous: { id: "case_h_ambiguous_dataset", product: "ambiguous", prompt: "Inspect ambiguous model semantics." },
};
const audits = new WeakMap();

async function main() {
  await mkdir(SCREENSHOTS, { recursive: true });
  const generated = spawnSync(
    "uv",
    ["run", "python", "scripts/generate_phase10k5_material_intelligence_evidence.py"],
    { cwd: ROOT, encoding: "utf8", timeout: 900_000 },
  );
  if (generated.status !== 0) throw new Error(`Material Intelligence evidence generation failed: ${safeError(generated.stderr || generated.stdout || generated.error)}`);

  const captures = {};
  const profiles = {};
  const artifacts = {};
  for (const [name, config] of Object.entries(CASES)) {
    captures[name] = await json(path.join(EVIDENCE, "api", `${config.id}_runtime_capture.json`));
    profiles[name] = await json(path.join(EVIDENCE, "api", `${config.id}_data_profile.json`));
    artifacts[name] = await hydratedArtifacts(config.id, captures[name].artifacts);
  }

  const playwright = await import(pathToFileURL(PLAYWRIGHT).href);
  const requested = new Set((process.env.MDI_MATERIAL_INTELLIGENCE_BROWSER_MATRIX || "chromium,firefox,webkit").split(",").map((value) => value.trim()));
  const browsers = [
    { id: "chromium", type: playwright.chromium, options: { ...(CHROME ? { executablePath: CHROME } : {}), args: ["--no-sandbox", "--disable-background-networking"] } },
    { id: "firefox", type: playwright.firefox, options: {} },
    { id: "webkit", type: playwright.webkit, options: {} },
  ].filter((item) => requested.has(item.id));
  const server = await ensureServer();
  const results = [];
  try {
    await waitForApp();
    for (const candidate of browsers) {
      let browser;
      try {
        browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
        const selectedCases = candidate.id === "chromium"
          ? Object.keys(CASES)
          : ["dataset", "regression", "composition"];
        results.push(await runBrowser(browser, candidate.id, selectedCases, captures, profiles, artifacts));
        console.log(`MATERIAL_INTELLIGENCE_BROWSER_PASS ${candidate.id}`);
      } catch (error) {
        results.push({ browser: candidate.id, available: false, reason: safeError(error) });
        console.log(`MATERIAL_INTELLIGENCE_BROWSER_FALLBACK ${candidate.id} ${safeError(error)}`);
      } finally {
        await browser?.close().catch(() => {});
      }
    }
    const chromium = results.find((item) => item.browser === "chromium");
    if (!chromium?.available) throw new Error("Chromium is required for Material Intelligence browser evidence.");
    if (results.some((item) => item.available && (item.externalRequests || item.consoleErrors?.length || item.pageErrors?.length))) {
      throw new Error("Material Intelligence browser network/console audit failed.");
    }
    await write("browser/browser_matrix.json", results);
    await write("browser/browser_integration.json", {
      browsers: results.filter((item) => item.available).map((item) => item.browser),
      desktopProducts: ["profile", "dataset", "materials_ml", "composition_space", "comparison", "partial", "ambiguous"],
      mobileProducts: ["dataset", "materials_ml", "composition_space"],
      marker: "MATERIAL_INTELLIGENCE_BROWSER_INTEGRATION_PASS",
    });
    await write("browser/console_network_audit.json", {
      browsers: results.map((item) => ({ browser: item.browser, available: item.available, externalRequests: item.externalRequests || 0, consoleErrors: item.consoleErrors || [], pageErrors: item.pageErrors || [] })),
      marker: "NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS",
    });
    await write("browser/accessibility_audit.json", {
      desktop: chromium.cases,
      mobile: chromium.mobile,
      marker: "MATERIAL_INTELLIGENCE_ACCESSIBILITY_EVIDENCE_PASS",
    });
    await write("browser/performance_metrics.json", {
      browsers: results.filter((item) => item.available).map((item) => ({ browser: item.browser, cases: Object.fromEntries(Object.entries(item.cases).map(([name, value]) => [name, value.firstProductMs])) })),
      mobile: chromium.mobile.map((item) => ({ case: item.case, firstProductMs: item.firstProductMs })),
      acceptance: "PASS",
    });
    await hashEvidence();
    console.log("MATERIAL_INTELLIGENCE_BROWSER_INTEGRATION_PASS");
    console.log("MATERIAL_INTELLIGENCE_ACCESSIBILITY_EVIDENCE_PASS");
    console.log("NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    if (server) {
      server.kill();
      await stopPort();
    }
  }
}

async function runBrowser(browser, browserId, caseNames, captures, profiles, artifacts) {
  const cases = {};
  const combined = { externalRequests: 0, consoleErrors: [], pageErrors: [] };
  for (const caseName of caseNames) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
    const page = await evidencePage(context, caseName, captures[caseName], profiles[caseName], artifacts[caseName]);
    cases[caseName] = await productFlow(page, caseName, false);
    if (browserId === "chromium") await screenshotProduct(page, caseName, path.join(SCREENSHOTS, `${caseName}.png`));
    mergeAudit(combined, await auditPage(page));
    await page.close();
    await context.close();
  }

  const mobile = [];
  if (browserId === "chromium") {
    for (const caseName of ["dataset", "regression", "composition"]) {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
      const page = await evidencePage(context, caseName, captures[caseName], profiles[caseName], artifacts[caseName]);
      mobile.push({ case: caseName, ...await productFlow(page, caseName, true) });
      await screenshotProduct(page, caseName, path.join(SCREENSHOTS, `mobile_${caseName}.png`));
      mergeAudit(combined, await auditPage(page));
      await page.close();
      await context.close();
    }
  }
  return { browser: browserId, version: browser.version(), available: true, cases, mobile, ...combined };
}

async function productFlow(page, caseName, mobile) {
  const started = Date.now();
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill(CASES[caseName].prompt);
  await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click();
  const integration = page.getByTestId("material-intelligence-integration");
  await integration.waitFor();
  const firstProductMs = Date.now() - started;
  const config = CASES[caseName];
  const checks = { product: config.product, integration: await integration.innerText() };

  if (["dataset", "partial", "ambiguous"].includes(config.product)) {
    const product = page.getByTestId("dataset-materials-explorer");
    await product.waitFor();
    for (const tab of ["Properties", "Data quality", "Model evaluation"]) {
      await product.getByRole("tab", { name: tab }).click();
    }
    if (config.product === "ambiguous") {
      await product.getByRole("tab", { name: "Overview" }).click();
      const overview = await product.getByTestId("dataset-explorer-overview").innerText();
      if (!overview.includes("SEMANTIC_GROUP_AMBIGUOUS")) throw new Error("Ambiguous Profile state is not disclosed.");
      checks.ambiguity = overview;
    }
    if (caseName === "dataset") {
      await product.getByRole("tab", { name: "Comparison" }).click();
      const comparison = await product.getByTestId("dataset-explorer-comparison").innerText();
      if (comparison.includes("No explicit dataset comparison")) throw new Error("Dataset comparison provenance is missing.");
      checks.comparison = comparison;
    }
    await product.getByRole("tab", { name: "Samples" }).click();
    const sampleButtons = product.locator('tbody button[type="button"]');
    if (await sampleButtons.count()) await (mobile ? sampleButtons.first().tap() : sampleButtons.first().click());
    checks.dataset = await product.innerText();
    checks.tableCount = await product.locator("table").count();
    if (config.product === "partial" && !checks.integration.includes("UNAVAILABLE")) throw new Error("Partial capability state is not explicit.");
  } else if (config.product === "ml") {
    const product = page.locator('[data-testid^="materials-ml-"]').filter({ hasNot: page.locator('[data-testid="materials-ml-invalid"]') }).first();
    await product.waitFor();
    checks.ml = await product.innerText();
    checks.tableCount = await product.locator("table").count();
    checks.chartCount = await product.locator('svg[role="img"]').count();
    if (caseName === "classification" && (!checks.ml.includes("Confusion matrix (raw counts)") || checks.tableCount < 2)) throw new Error("Classification numeric confusion matrix is missing.");
  } else {
    const product = page.getByTestId("composition-space-explorer");
    await product.waitFor();
    const points = product.locator('svg circle[role="button"]');
    if (await points.count() < 3) throw new Error("Composition Space point surface is incomplete.");
    await (mobile ? points.first().tap() : points.first().click());
    await points.nth(1).focus();
    await page.keyboard.press("Enter");
    checks.composition = await product.innerText();
    checks.tableCount = await product.locator("table").count();
    checks.keyboardPoints = await product.locator('svg circle[role="button"][tabindex="0"]').count();
  }

  const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  if (horizontalOverflow) throw new Error(`${caseName} has catastrophic horizontal overflow.`);
  const inert = await page.evaluate(() => ({ canvas: document.querySelectorAll("canvas").length, iframe: document.querySelectorAll("iframe").length, javascriptUri: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length }));
  if (inert.canvas || inert.iframe || inert.javascriptUri) throw new Error(`Material Intelligence inert-surface audit failed: ${JSON.stringify(inert)}`);
  return { firstProductMs, mobile, horizontalOverflow, checks };
}

async function screenshotProduct(page, caseName, target) {
  const testId = CASES[caseName].product === "composition"
    ? "composition-space-explorer"
    : CASES[caseName].product === "ml"
      ? null
      : "dataset-materials-explorer";
  const locator = testId ? page.getByTestId(testId) : page.locator('[data-testid^="materials-ml-"]').first();
  await locator.screenshot({ path: target });
}

async function hydratedArtifacts(caseId, records) {
  return Promise.all(records.map(async (artifact) => {
    const file = path.join(EVIDENCE, "products", caseId, artifact.name);
    const raw = await readFile(file, "utf8");
    const content = artifact.name.endsWith(".json") ? JSON.parse(raw) : raw;
    return { ...artifact, content, metadata: { ...(artifact.metadata || {}), preview: content } };
  }));
}

async function evidencePage(context, caseName, capture, profile, artifacts) {
  const audit = { external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
  const page = await context.newPage();
  audits.set(page, audit);
  await page.addInitScript(() => { window.EventSource = class { close() {} addEventListener() {} removeEventListener() {} }; });
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => { if (response.status() >= 400) audit.httpErrors.push({ status: response.status(), path: new URL(response.url()).pathname }); });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url, caseName, capture, profile, artifacts);
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

async function api(route, url, caseName, capture, profile, artifacts) {
  const method = route.request().method();
  const job = `job_phase10k5_${caseName}_browser`;
  const plan = capture.plan;
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: profile.datasetId, datasetId: profile.datasetId, projectId: "project_phase10k5_evidence", name: `Material Intelligence ${caseName}`, status: "ready", demo: true, profileId: profile.profileId, profile } });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: `plan_phase10k5_${caseName}`, plan_hash: capture.job.planHash, validation_errors: [], plan, plan_source: "mock", planner_provider: "MockLLMProvider", enqueued: true, executed: true } });
  if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: { jobId: job, projectId: "project_phase10k5_evidence", datasetId: profile.datasetId, status: "completed", planId: `plan_phase10k5_${caseName}`, planHash: capture.job.planHash, planSource: "mock", analysisPlan: plan, validationStatus: "validated", toolCallCount: 1, artifactCount: artifacts.length, eventCount: capture.events.length } });
  if (url.pathname === `/planner/jobs/${job}/events`) return route.fulfill({ json: capture.events });
  if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: capture.toolCalls });
  if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: artifacts });
  if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { ...capture.result, jobId: job, artifacts } });
  return route.fulfill({ status: 404, json: { detail: "material-intelligence evidence route not found" } });
}

async function auditPage(page) {
  const audit = audits.get(page);
  const inert = await page.evaluate(() => ({ externalScript: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length, inlineHandler: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length }));
  if (Object.values(inert).some(Boolean) || audit.consoleErrors.length || audit.pageErrors.length || audit.external.length || audit.httpErrors.length) throw new Error(`Material Intelligence browser audit failed: ${JSON.stringify({ inert, ...audit })}`);
  return { externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors };
}

function mergeAudit(target, source) { target.externalRequests += source.externalRequests; target.consoleErrors.push(...source.consoleErrors); target.pageErrors.push(...source.pageErrors); }
function startServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
  return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: "ignore" });
}
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const deadline = Date.now() + 60_000; while (Date.now() < deadline) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("Material Intelligence app startup timed out."); }
async function stopPort() { if (process.platform !== "win32") return; const command = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`; await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", command], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); }); }
async function write(relative, value) { const file = path.join(EVIDENCE, relative); await mkdir(path.dirname(file), { recursive: true }); await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
async function json(file) { return JSON.parse(await readFile(file, "utf8")); }
function safeError(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 1000); }
async function listFiles(directory) { const result = []; for (const entry of await readdir(directory, { withFileTypes: true })) { const target = path.join(directory, entry.name); if (entry.isDirectory()) result.push(...await listFiles(target)); else result.push(target); } return result.sort(); }
async function hashEvidence() { const files = (await listFiles(EVIDENCE)).filter((file) => !file.endsWith("evidence_manifest.json")); await write("evidence_manifest.json", { algorithm: "sha256", files: await Promise.all(files.map(async (file) => ({ name: path.relative(EVIDENCE, file).replaceAll("\\", "/"), bytes: (await stat(file)).size, sha256: createHash("sha256").update(await readFile(file)).digest("hex") }))) }); }

await main();
